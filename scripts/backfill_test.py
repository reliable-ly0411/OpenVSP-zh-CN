"""Offline regression tests; never execute a downloaded or generated binary."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
import unittest
import sys
import xml.etree.ElementTree as ET
from unittest.mock import patch
import zipfile

from backfill_diagnostics import macho_regions, summarize_matches, symbol_categories
from backfill_gui import capture, prepare_model, GUI_INPUT_DIRECTORY, gui_executable
from backfill_plan import matrix, PLATFORMS, validate_pilot
from backfill_package import verify
from backfill_verify import privacy_scan, rpaths, dependencies, audit_native, bundle_mac, minimum_macos, python_smoke, parse_minos, cli_help, install_legacy_fonts, digest




class LegacyFontTests(unittest.TestCase):
    def test_only_old_linux_gets_supplements(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertIsNone(install_legacy_fonts(root, '3.53.0', True))
            self.assertIsNone(install_legacy_fonts(root, '3.51.2', False))
            self.assertFalse(list(root.iterdir()))

    def test_hash_modes_original_and_duplicate_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'vsp').write_bytes(b'unchanged fixture')
            original = digest(root/'vsp')
            report = install_legacy_fonts(root, '3.51.2', True)
            self.assertEqual(digest(root/'vsp'), original)
            for record in report['files']:
                f = root/record['file']
                self.assertEqual(digest(f), record['sha256'])
                self.assertEqual(oct(f.stat().st_mode & 0o777), record['mode'])
            with self.assertRaises(ValueError): install_legacy_fonts(root, '3.51.2', True)

    def test_configuration_retains_system_fonts_and_exact_aliases(self):
        tree = ET.parse(Path(__file__).with_name('backfill_legacy_fonts.conf'))
        self.assertEqual(tree.find('include').text, '/etc/fonts/fonts.conf')
        aliases = {}
        for rule in tree.findall('match'):
            test = rule.find('test')
            self.assertEqual(test.attrib, {'name': 'family', 'qual': 'any', 'compare': 'eq'})
            aliases[test.find('string').text] = rule.find('edit/string').text
        self.assertEqual(set(aliases), {'sans', 'sans-serif', 'Helvetica', 'mono', 'monospace', 'Courier'})
        self.assertEqual(aliases['sans'], 'Noto Sans CJK SC')
        self.assertEqual(aliases['mono'], 'Noto Sans Mono CJK SC')

    def test_launcher_forwards_args_and_scopes_environment_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='font fixture ') as tmp:
            root = Path(tmp); bindir = root/'fake commands'; bindir.mkdir()
            # Our own inert fixtures, never downloaded native binaries.
            (root/'vsp').write_text('#!' + sys.executable + '\nimport os,sys,json\nprint(json.dumps([sys.argv[1:],os.environ.get("FONTCONFIG_FILE")]))\n')
            (root/'vsp').chmod(0o755)
            fc = bindir/'fc-match'
            fc.write_text('#!/bin/sh\nfor last do :; done\ncase "$last" in mono|monospace|Courier) printf "Noto Sans Mono CJK SC";; *) printf "Noto Sans CJK SC";; esac\n')
            fc.chmod(0o755)
            install_legacy_fonts(root, '3.51.3', True)
            env = dict(os.environ, PATH=str(bindir)+os.pathsep+os.environ['PATH'], FONTCONFIG_FILE='original')
            args = ['space model.vsp3', '--flag', '中文', '']
            output = subprocess.check_output([str(root/'vsp-zh-CN'), *args], env=env, text=True)
            self.assertEqual(json.loads(output), [args, str(root/'openvsp-zh-fonts.conf')])
            self.assertEqual(env['FONTCONFIG_FILE'], 'original')
            fc.write_text('#!/bin/sh\nprintf "Wrong Font"\n')
            failure = subprocess.run([str(root/'vsp-zh-CN')], env=env, capture_output=True, text=True)
            self.assertNotEqual(failure.returncode, 0)
            self.assertIn('fonts-noto-cjk', failure.stderr)
            self.assertEqual(failure.stdout, '')

    @unittest.skipUnless(shutil.which('fc-match'), 'Fontconfig unavailable')
    def test_real_fontconfig_maps_all_actual_fltk_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, XDG_CACHE_HOME=tmp)
            for family in ('Noto Sans CJK SC', 'Noto Sans Mono CJK SC'):
                found = subprocess.check_output(['fc-match', '--format', '%{family}', family], env=env, stderr=subprocess.DEVNULL, text=True)
                if family not in found:
                    self.skipTest('Noto CJK unavailable; native CI launcher enforces every alias')
            env['FONTCONFIG_FILE'] = str(Path(__file__).with_name('backfill_legacy_fonts.conf').resolve())
            for alias in ('sans', 'sans-serif', 'Helvetica', 'mono', 'monospace', 'Courier'):
                expected = 'Noto Sans Mono CJK SC' if alias in ('mono', 'monospace', 'Courier') else 'Noto Sans CJK SC'
                actual = subprocess.check_output(['fc-match', '--format', '%{family}', alias], env=env, stderr=subprocess.DEVNULL, text=True)
                self.assertIn(expected, actual)

    def test_gui_uses_same_packaged_launcher_only_for_old_versions(self):
        root = Path('/neutral')
        self.assertEqual(gui_executable(root, '3.51.2'), root/'vsp-zh-CN')
        self.assertEqual(gui_executable(root, '3.51.3'), root/'vsp-zh-CN')
        self.assertEqual(gui_executable(root, '3.53.0'), root/'vsp')

class CliHelpTests(unittest.TestCase):
    @patch('backfill_verify.run', return_value='用法: vsp')
    def test_normal_help_requires_no_retry(self, command):
        with tempfile.TemporaryDirectory() as tmp:
            result = cli_help(Path('vsp'), '3.51.2', tmp, {}, Path(tmp)/'diag', True)
            self.assertEqual(result['initial_exit_code'], 0)
            self.assertEqual(command.call_count, 1)

    @patch('backfill_verify.run')
    def test_only_exact_old_display_failure_can_retry(self, command):
        command.side_effect = [subprocess.CalledProcessError(1, ['vsp'], output="Can't open display: \n"), '用法: vsp']
        with tempfile.TemporaryDirectory() as tmp:
            result = cli_help(Path('vsp'), '3.51.2', tmp, {}, Path(tmp)/'diag', True)
            self.assertEqual(result['retry_exit_code'], 0)
            self.assertEqual(command.call_args.args[0], 'xvfb-run')

    def test_unrelated_failure_modern_version_and_mac_stay_failed(self):
        for version, linux, output in [('3.51.2', True, 'private secret /runner/path'),
                                        ('3.53.0', True, "Can't open display:"),
                                        ('3.51.2', False, "Can't open display:")]:
            with tempfile.TemporaryDirectory() as tmp, patch('backfill_verify.run') as command:
                command.side_effect = subprocess.CalledProcessError(1, ['vsp'], output=output)
                with self.assertRaises(ValueError):
                    cli_help(Path('vsp'), version, tmp, {}, Path(tmp)/'diag', linux)
                self.assertEqual(command.call_count, 1)
                report = (Path(tmp)/'diag/runtime.json').read_text()
                self.assertNotIn(output, report)

    @patch('backfill_verify.run')
    def test_failed_xvfb_retry_still_fails(self, command):
        command.side_effect = [subprocess.CalledProcessError(1, ['vsp'], output="Can't open display:"),
                               subprocess.CalledProcessError(2, ['vsp'], output='private values')]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                cli_help(Path('vsp'), '3.51.3', tmp, {}, Path(tmp)/'diag', True)
            report = json.loads((Path(tmp)/'diag/runtime.json').read_text())
            self.assertEqual(report['xvfb_retry_exit_code'], 2)
            self.assertNotIn('private values', json.dumps(report))

    def test_timeout_or_missing_launcher_never_leaks_or_passes(self):
        for retry in (False, True):
            for error in (subprocess.TimeoutExpired('/private/workspace/vsp', 120, output='private'),
                          FileNotFoundError('/private/workspace/launcher')):
                with tempfile.TemporaryDirectory() as tmp, patch('backfill_verify.run') as command:
                    failures = [error]
                    if retry:
                        failures.insert(0, subprocess.CalledProcessError(1, ['vsp'], output="Can't open display:"))
                    command.side_effect = failures
                    with self.assertRaises(ValueError) as raised:
                        cli_help(Path('vsp'), '3.51.2', tmp, {}, Path(tmp)/'diag', True)
                    self.assertEqual(command.call_count, 2 if retry else 1)
                    report = (Path(tmp)/'diag/runtime.json').read_text()
                    self.assertNotIn('private', report + str(raised.exception))
                    self.assertIn('xvfb-retry' if retry else 'initial', report)

    @patch('backfill_verify.run')
    def test_non_one_exit_never_retries(self, command):
        command.side_effect = subprocess.CalledProcessError(2, ['vsp'], output="Can't open display:")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                cli_help(Path('vsp'), '3.51.2', tmp, {}, Path(tmp)/'diag', True)
            self.assertEqual(command.call_count, 1)

    @patch('backfill_verify.run', return_value='Usage: vsp')
    def test_zero_exit_without_chinese_help_still_fails(self, command):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                cli_help(Path('vsp'), '3.51.2', tmp, {}, Path(tmp)/'diag', True)


class BackfillWorkflowTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1]/'.github/workflows/backfill-platforms.yml'
        self.workflow = path.read_text(encoding='utf-8')
        self.plan, self.build = self.workflow.split('\n  build:\n', 1)

    def test_pull_requests_keep_only_offline_regression(self):
        self.assertIn('\n  pull_request:\n', self.workflow)
        self.assertIn('python3 -m unittest discover -s scripts -p backfill_test.py -v', self.plan)
        self.assertNotRegex(self.plan, r'(?m)^    if:')
        self.assertNotIn('backfill_build.sh', self.plan)
        self.assertNotIn('cmake --build', self.plan)

    def test_native_planning_and_build_jobs_require_manual_dispatch(self):
        # Job-level if is evaluated before matrix expansion. Guard both the
        # matrix producer and consumer so a PR cannot allocate native runners.
        self.assertIn("      - id: plan\n        if: github.event_name == 'workflow_dispatch'\n", self.plan)
        self.assertTrue(self.build.startswith("    if: github.event_name == 'workflow_dispatch'\n"))

    def test_manual_historical_scopes_and_read_only_permissions_remain(self):
        self.assertIn('\n  workflow_dispatch:\n', self.workflow)
        self.assertIn('options: [pilot, legacy-linux, all]', self.workflow)
        self.assertIn("SCOPE: ${{ inputs.scope || 'pilot' }}", self.plan)
        self.assertIn('permissions:\n  contents: read\n  actions: read\n', self.workflow)
        self.assertNotIn('contents: write', self.workflow)
        self.assertNotIn('gh release', self.workflow)


class PlanTests(unittest.TestCase):
    def test_legacy_linux_has_only_two_fixed_targets(self):
        jobs = matrix('legacy-linux')['include']
        self.assertEqual(len(jobs), 2)
        self.assertEqual({j['runner'] for j in jobs}, {'ubuntu-24.04-arm'})
        self.assertEqual({j['arch'] for j in jobs}, {'aarch64'})
        self.assertEqual({(j['version'], j['sha']) for j in jobs}, {
            ('3.51.2', '24f270c1ffc52e7477b2305669172ba49b49b114'),
            ('3.51.3', '4b523612b030d8d087dba49f79a716712496c403')})
        for invalid in ('3.51.2', 'ubuntu-24.04-arm', 'legacy-linux,all', '*'):
            with self.assertRaises(ValueError): matrix(invalid)

    def test_pilot_has_exactly_three_platforms(self):
        jobs = matrix('pilot')['include']
        self.assertEqual(len(jobs), 3)
        self.assertEqual({j['version'] for j in jobs}, {'3.53.0'})
        self.assertEqual({j['runner'] for j in jobs}, {'macos-14', 'macos-15-intel', 'ubuntu-24.04-arm'})

    def test_all_has_fifteen_immutable_unique_targets(self):
        jobs = matrix('all')['include']
        self.assertEqual(len(jobs), 15)
        self.assertEqual(len({(j['sha'], j['platform']) for j in jobs}), 15)
        for j in jobs:
            self.assertRegex(j['sha'], '^[a-f0-9]{40}$')
            self.assertIn(j['python'], ('3.11', '3.12'))

    def test_invalid_scope(self):
        with self.assertRaises(ValueError):
            matrix('some-ref; echo unsafe')

    def pilot(self):
        return dict(conclusion='success', status='completed', repository={'full_name': 'a/b'},
                    path='.github/workflows/backfill-platforms.yml', head_sha='a'*40)

    def jobs(self):
        return [dict(name=f"3.53.0 / {p['platform']}", conclusion='success') for p in PLATFORMS]

    def test_reject_wrong_workflow(self):
        run = self.pilot(); run['path'] = 'other.yml'
        with self.assertRaises(ValueError):
            validate_pilot(run, self.jobs(), 'a/b')

    def test_reject_partial_pilot(self):
        with self.assertRaises(ValueError):
            validate_pilot(self.pilot(), self.jobs()[:2], 'a/b')

    @patch('backfill_plan.subprocess.run')
    @patch('backfill_plan.subprocess.check_output')
    def test_reject_changed_tooling(self, output, command):
        command.return_value.returncode = 0
        output.return_value = 'scripts/backfill_verify.py\n'
        with self.assertRaises(ValueError):
            validate_pilot(self.pilot(), self.jobs(), 'a/b')

    @patch('backfill_plan.subprocess.run')
    @patch('backfill_plan.subprocess.check_output')
    def test_accept_same_tooling(self, output, command):
        command.return_value.returncode = 0; output.return_value = ''
        validate_pilot(self.pilot(), self.jobs(), 'a/b')


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root/'source'; self.source.mkdir()
        self.files = ['README.md', 'README_zh-CN.md', 'AGENTS.md', 'LICENSE', 'CHANGELOG.md',
                      'vspIcon.png', 'examples/demo.vsp3', 'src/help/html/demo.html',
                      'src/help/vsp_help', 'src/help/github-pandoc.css', 'src/help/images/demo.png']
        for name in self.files:
            p = self.source/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(name.encode())
        def git(*args):
            subprocess.run(['git', '-C', str(self.source), *args], check=True, capture_output=True)
        git('init'); git('add', '.'); git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'fixture')
        self.archive = self.root/'test.zip'

    def tearDown(self):
        self.tmp.cleanup()

    def make_archive(self, mutate=None):
        entries = {}
        for name in self.files:
            dest = name
            if name.startswith('examples/'):
                dest = 'Official_Examples/' + name.removeprefix('examples/')
            elif name.startswith('src/help/html/'):
                dest = 'help/' + Path(name).name
            elif name.startswith('src/help/'):
                dest = name.removeprefix('src/')
            entries['OpenVSP/' + dest] = name.encode()
        for name in ('vsp', 'vspscript', 'vspaero', 'vspviewer', 'vsploads'):
            entries['OpenVSP/' + name] = b'fixture, never executable'
        if mutate:
            mutate(entries)
        with zipfile.ZipFile(self.archive, 'w') as z:
            for name, data in entries.items():
                z.writestr(name, data)

    def test_exact_source_package_passes(self):
        self.make_archive(); self.assertEqual(verify(self.archive, self.source), len(self.files))

    def test_reject_changed_examples(self):
        self.make_archive(lambda d: d.update({'OpenVSP/Official_Examples/demo.vsp3': b'changed'}))
        with self.assertRaises(ValueError):
            verify(self.archive, self.source)

    def test_reject_changed_help_image(self):
        self.make_archive(lambda d: d.update({'OpenVSP/help/images/demo.png': b'changed'}))
        with self.assertRaises(ValueError):
            verify(self.archive, self.source)

    def test_modified_worktree_does_not_change_baseline(self):
        self.make_archive()
        (self.source/'README.md').write_text('modified')
        verify(self.archive, self.source)

    def test_reject_zip_path_traversal(self):
        self.make_archive(lambda d: d.update({'OpenVSP/../escape': b'x'}))
        with self.assertRaises(ValueError):
            verify(self.archive, self.source)

    def test_reject_missing_program(self):
        self.make_archive(lambda d: d.pop('OpenVSP/vsp'))
        with self.assertRaises(ValueError):
            verify(self.archive, self.source)


class PrivacyTests(unittest.TestCase):
    def test_private_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'data').write_bytes(b'prefix /home/private/build trailing')
            with self.assertRaises(ValueError):
                privacy_scan(root, [b'/home/private'])

    def test_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'data').write_bytes(b'ghp_' + b'x'*35)
            with self.assertRaises(ValueError):
                privacy_scan(root, [])

    def test_diagnostic_does_not_echo_private_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'vsp').write_bytes(b'/Users/privateperson/work/source.o')
            with self.assertRaises(ValueError) as caught:
                privacy_scan(root, [b'/Users/privateperson'])
            self.assertIn('Runner/workspace path remains', str(caught.exception))
            self.assertNotIn('privateperson', str(caught.exception))

    def test_safe_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'LICENSE').write_text('OpenVSP public license')
            privacy_scan(root, [])

    def test_escaping_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'link').symlink_to('/tmp')
            with self.assertRaises(ValueError):
                privacy_scan(root, [])


class MachOParsingTests(unittest.TestCase):
    @patch('backfill_verify.run')
    def test_rpaths_with_spaces(self, command):
        command.return_value = 'Load command 1\n cmd LC_RPATH\n cmdsize 40\n path /test path/lib (offset 12)\n'
        self.assertEqual(rpaths(Path('test')), ['/test path/lib'])

    @patch('backfill_verify.run')
    def test_dependency_does_not_include_dylib_identity(self, command):
        command.side_effect = ['test:\n@rpath/test.dylib\n',
                               'test:\n\t@rpath/test.dylib (compatibility version 1.0.0, current version 1.0.0)\n\t/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1.0.0)\n']
        self.assertEqual(dependencies(Path('test')), ['/usr/lib/libSystem.B.dylib'])

    @patch('backfill_verify.run')
    def test_wrong_elf_architecture_fails(self, command):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'vsp').write_text('test')
            command.side_effect = ['ELF 64-bit', 'Machine: Advanced Micro Devices X86-64']
            with self.assertRaises(ValueError):
                audit_native(root, 'aarch64', False)



class MacClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base/'package'; self.root.mkdir()
        self.exe = self.root/'vsp'; self.exe.write_bytes(b'fixture')
        self.libs = self.base/'external'; self.libs.mkdir()
        self.a = self.libs/'liba.dylib'; self.a.write_bytes(b'lib-a')
        self.b = self.libs/'libb.dylib'; self.b.write_bytes(b'lib-b')

    def tearDown(self):
        self.tmp.cleanup()

    def macho_files(self, root):
        return [self.exe] + sorted((root/'lib').glob('*.dylib'))

    @patch('backfill_verify.run')
    @patch('backfill_verify.rpaths')
    @patch('backfill_verify.dependencies')
    @patch('backfill_verify.machos')
    def test_recursive_closure_relocated_and_signed(self, machos, deps, rpaths_mock, commands):
        machos.side_effect = self.macho_files
        rpaths_mock.return_value = [str(self.libs)]
        def edges(path):
            if path == self.exe: return ['@rpath/liba.dylib']
            if path == self.a: return ['@loader_path/libb.dylib']
            if path == self.b: return ['/usr/lib/libSystem.B.dylib']
            raise AssertionError(path)
        deps.side_effect = edges; commands.return_value = ''
        graph, notices = bundle_mac(self.root)
        self.assertEqual(len(graph), 3)
        self.assertEqual(len(list((self.root/'lib').glob('*.dylib'))), 2)
        calls = [c.args for c in commands.call_args_list]
        self.assertEqual(sum(c[:2] == ('strip', '-S') for c in calls), 3)
        self.assertEqual(sum(c[:4] == ('codesign', '--force', '--sign', '-') for c in calls), 3)
        for i, call in enumerate(calls):
            if call[:4] == ('codesign', '--force', '--sign', '-'):
                self.assertEqual(calls[i-1], ('strip', '-S', call[-1]))
        self.assertEqual(sum(c[:3] == ('codesign', '--verify', '--strict') for c in calls), 3)
        changes = [c for c in calls if c[:2] == ('install_name_tool', '-change')]
        self.assertEqual(len(changes), 2)
        self.assertTrue(all(c[3].startswith('@loader_path/') for c in changes))
        self.assertEqual(set(notices), {'liba.dylib', 'libb.dylib'})

    @patch('backfill_verify.run')
    @patch('backfill_verify.rpaths', return_value=[])
    @patch('backfill_verify.dependencies')
    @patch('backfill_verify.machos')
    def test_unresolved_dependency_fails_before_signing(self, machos, deps, paths, commands):
        machos.return_value = [self.exe]; deps.return_value = ['@rpath/missing.dylib']
        with self.assertRaises(ValueError): bundle_mac(self.root)
        commands.assert_not_called()

    @patch('backfill_verify.run')
    @patch('backfill_verify.rpaths', return_value=[])
    @patch('backfill_verify.dependencies')
    @patch('backfill_verify.machos')
    def test_external_framework_fails_closed(self, machos, deps, paths, commands):
        machos.return_value = [self.exe]; deps.return_value = ['/external/Foo.framework/Versions/A/Foo']
        with self.assertRaisesRegex(ValueError, 'framework'): bundle_mac(self.root)
        commands.assert_not_called()

    @patch('backfill_verify.run')
    @patch('backfill_verify.rpaths', return_value=[])
    @patch('backfill_verify.dependencies')
    @patch('backfill_verify.machos')
    def test_system_framework_is_not_copied(self, machos, deps, paths, commands):
        machos.return_value = [self.exe]; deps.return_value = ['/System/Library/Frameworks/Cocoa.framework/Versions/A/Cocoa']
        commands.return_value = ''
        graph, _ = bundle_mac(self.root)
        self.assertEqual(len(graph), 1)
        self.assertEqual(list((self.root/'lib').iterdir()), [])

    @patch('backfill_verify.run')
    @patch('backfill_verify.rpaths', return_value=[])
    @patch('backfill_verify.dependencies', return_value=[])
    @patch('backfill_verify.machos')
    def test_signature_failure_stops_bundle(self, machos, deps, paths, commands):
        machos.return_value = [self.exe]
        def fail_codesign(*args, **kwargs):
            if args[0] == 'codesign':
                raise subprocess.CalledProcessError(1, ['codesign'])
            return ''
        commands.side_effect = fail_codesign
        with self.assertRaises(subprocess.CalledProcessError): bundle_mac(self.root)
        self.assertFalse((self.root/'third-party-dependencies.json').exists())


class MinimumAndPythonTests(unittest.TestCase):
    def test_build_version_ignores_linker_tool_version(self):
        fixture = """/tmp/vsp:
Load command 9
      cmd LC_BUILD_VERSION
  cmdsize 32
 platform 1
    minos 14.0
      sdk 15.2
   ntools 1
     tool LD
  version 1109.8
Load command 10
          cmd LC_LOAD_DYLIB
      cmdsize 56
         name /usr/lib/libSystem.B.dylib (offset 24)
   time stamp 2 Thu Jan  1 00:00:02 1970
      current version 1351.0.0
compatibility version 1.0.0
"""
        self.assertEqual(parse_minos(fixture), ['14.0'])
        self.assertEqual(minimum_macos([{'minos': parse_minos(fixture)}], '14.7',
                                      'macOS-14-arm64-Python3.11')['maximum_macho_minimum'], '14.0')

    def test_legacy_version_min_command(self):
        fixture = """/tmp/legacy:
Load command 8
      cmd LC_VERSION_MIN_MACOSX
  cmdsize 16
  version 10.15
      sdk 11.3
Load command 9
      cmd LC_SOURCE_VERSION
  cmdsize 16
  version 900.7
"""
        self.assertEqual(parse_minos(fixture), ['10.15'])

    def test_aggregate_minos_numerically(self):
        result = minimum_macos([{'minos': ['10.15', '14.2']}, {'minos': ['14.1']}], '14.7', 'macOS-14-arm64-Python3.11')
        self.assertEqual(result['maximum_macho_minimum'], '14.2')

    def test_reject_minimum_newer_than_named_platform(self):
        with self.assertRaises(ValueError):
            minimum_macos([{'minos': ['15.0']}], '15.1', 'macOS-14-arm64-Python3.11')

    def test_reject_minimum_newer_than_host(self):
        with self.assertRaises(ValueError):
            minimum_macos([{'minos': ['14.8']}], '14.7', 'macOS-14-arm64-Python3.11')

    @patch('backfill_verify.run')
    def test_both_python_modules_run_in_separate_processes(self, command):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('_vsp.so', '_vsp_g.so'): (root/name).write_bytes(b'fixture')
            command.return_value = json.dumps(dict(version='3.53.0', interpreter_soabi='cpython-311-darwin', python='3.11.9'))
            checks = python_smoke(root, '3.53.0', tmp, {})
            self.assertEqual(len(checks), 2)
            self.assertEqual(command.call_count, 2)
            self.assertEqual({call.args[-1] for call in command.call_args_list}, {'_vsp', '_vsp_g'})

    def test_reject_missing_graphical_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'_vsp.so').write_bytes(b'fixture')
            with self.assertRaises(ValueError): python_smoke(root, '3.53.0', tmp, {})

class GuiEvidenceTests(unittest.TestCase):
    def test_gui_input_path_is_neutral_and_workspace_independent(self):
        self.assertEqual(str(GUI_INPUT_DIRECTORY), '/tmp/openvsp-ui-evidence')
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'runner-workspace-model.vsp3'
            source.write_bytes(b'model')
            target = Path(tmp) / 'neutral'
            with patch('backfill_gui.GUI_INPUT_DIRECTORY', target):
                model = prepare_model(source)
                self.assertEqual(model.parent, target)
                self.assertEqual(model.name, 'localization-smoke.vsp3')
                self.assertEqual(model.read_bytes(), b'model')
                with self.assertRaises(FileExistsError):
                    prepare_model(source)

    def test_missing_package_does_not_create_screenshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                capture(root, root/'missing.vsp3', root/'evidence')
            self.assertFalse((root/'evidence').exists())

    @patch('backfill_gui.subprocess.Popen')
    def test_early_gui_exit_is_not_accepted(self, popen):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'vsp').write_text('fixture')
            model = root/'sample.vsp3'; model.write_text('fixture')
            popen.return_value.poll.return_value = 1
            with self.assertRaises(RuntimeError): capture(root, model, root/'evidence')
            self.assertFalse(list((root/'evidence').glob('*.png')))
            self.assertEqual(popen.call_args.args[0][-1], model.name)
            self.assertEqual(popen.call_args.kwargs['cwd'], model.parent)

class PrivacyDiagnosticTests(unittest.TestCase):
    def test_catalog_classification_never_emits_path_value(self):
        prefix = b'/Users/privateperson/work/project'
        data = b'file://' + prefix + b'/source/buildlibs/LIBXML2-prefix/etc/xml/catalog\0'
        report = summarize_matches(data, [prefix, b'/Users/privateperson'], [(0, len(data), '__TEXT/__cstring')])
        self.assertEqual(len(report), 2)
        self.assertTrue(all(r['path_category'] == 'xml-default-catalog' for r in report))
        text = json.dumps(report)
        self.assertNotIn('privateperson', text)
        self.assertNotIn('LIBXML2-prefix', text)
        self.assertIn('__TEXT/__cstring', text)

    def test_macho_section_offsets_and_symbol_table(self):
        fixture = """Load command 0
      cmd LC_SEGMENT_64
Section
  sectname __cstring
   segname __TEXT
      addr 0x0000000100001000
      size 0x0000000000000020
    offset 4096
Load command 1
     cmd LC_SYMTAB
  stroff 8192
 strsize 128
"""
        self.assertEqual(macho_regions(fixture), [(4096, 32, '__TEXT/__cstring'), (8192, 128, 'LC_SYMTAB/string-table')])

    def test_nm_summary_only_fixed_categories(self):
        result = symbol_categories('000000 - 00 0000 OSO /Users/private/file.o\n', [b'/Users/private'])
        self.assertEqual(result, {'N_OSO': 1, 'N_SO': 0, 'other': 0})
        self.assertNotIn('private', json.dumps(result))

    def test_privacy_failure_writes_only_value_free_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'package'; root.mkdir()
            (root/'vsp').write_bytes(b'file:///private/build/etc/xml/catalog\0')
            diagnostic = Path(tmp)/'diagnostics'
            with self.assertRaises(ValueError):
                privacy_scan(root, [b'/private/build'], diagnostic)
            text = (diagnostic/'privacy.json').read_text()
            self.assertNotIn('/private/build', text)
            self.assertEqual(json.loads(text)['matches'][0]['path_category'], 'xml-default-catalog')
            self.assertEqual(list(diagnostic.iterdir()), [diagnostic/'privacy.json'])

class LibxmlToolchainTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cmake'), 'CMake unavailable in offline workspace')
    def test_fresh_child_inherits_scoped_toolchain_without_changing_other_projects(self):
        toolchain = Path(__file__).with_name('backfill_libxml_toolchain.cmake').resolve()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for path, expected in [('LIBXML2-prefix/src/LIBXML2', '/etc'), ('unrelated-project', 'unset')]:
                source = base/path; source.mkdir(parents=True)
                source.joinpath('CMakeLists.txt').write_text(
                    'cmake_minimum_required(VERSION 3.24)\nproject(Fixture NONE)\n'
                    'if(NOT DEFINED CMAKE_INSTALL_SYSCONFDIR)\nset(CMAKE_INSTALL_SYSCONFDIR unset)\nendif()\n'
                    'file(WRITE "${CMAKE_BINARY_DIR}/result.txt" "${CMAKE_INSTALL_SYSCONFDIR}")\n')
                build = source/'build'
                env = dict(os.environ, CMAKE_TOOLCHAIN_FILE=str(toolchain))
                if expected == '/etc':
                    parent = base/'parent'; parent.mkdir()
                    parent.joinpath('CMakeLists.txt').write_text(
                        'cmake_minimum_required(VERSION 3.24)\nproject(Parent NONE)\n'
                        'include(ExternalProject)\n'
                        'ExternalProject_Add(LIBXML2 SOURCE_DIR "' + source.as_posix() + '"\n'
                        ' BINARY_DIR "' + build.as_posix() + '"\n'
                        ' DOWNLOAD_COMMAND "" BUILD_COMMAND "" INSTALL_COMMAND "")\n')
                    parent_build = base/'parent-build'
                    subprocess.run(['cmake', '-S', str(parent), '-B', str(parent_build)], env=env,
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    subprocess.run(['cmake', '--build', str(parent_build)], env=env,
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                else:
                    subprocess.run(['cmake', '-S', str(source), '-B', str(build)], env=env,
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.assertEqual((build/'result.txt').read_text(), expected)

if __name__ == '__main__':
    unittest.main()
