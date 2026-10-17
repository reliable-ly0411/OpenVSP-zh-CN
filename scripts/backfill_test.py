"""Offline regression tests; never execute a downloaded or generated binary."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from backfill_gui import capture
from backfill_plan import matrix, PLATFORMS, validate_pilot
from backfill_package import verify
from backfill_verify import privacy_scan, rpaths, dependencies, audit_native, bundle_mac, minimum_macos, python_smoke, parse_minos


class PlanTests(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
