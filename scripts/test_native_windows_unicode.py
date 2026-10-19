"""Offline contracts for the single-family generated-fixture diagnosis."""
import copy
import errno
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from native_windows_unicode import (EXPECTED, SOURCE_BASELINE, SOURCE_PATCH_SHA256, STL_FILENAME,
                                    apply_patch, capture, compare, directory_records, path_record,
                                    probe, probe_case_passed, redact)


def reports():
    old = dict(phase='baseline', environment=dict(platform='Windows', acp=1252, oem=437),
               executable_sha256='a' * 64, cases=[
        dict(case='boundary', passed=True),
        dict(case='functional', exit_code=0, markers_passed=True,
             output_origin='actual subprocess capture',
             disk_error='stl-file-missing', expected=dict(exists=False),
             stdout=dict(bytes=300, sha256='f' * 64),
             files=[dict(name=STL_FILENAME.encode('utf-8').decode('cp1252'), file=True, bytes=100)])])
    new = dict(phase='patched', environment=dict(platform='Windows', acp=1252, oem=437),
               executable_sha256='b' * 64, passed=True)
    return old, new


def successful_probe_capture(command, directory, roots=()):
    _, mode, case = command
    opened = case not in ('blocked', 'missing', 'invalid')
    if opened:
        (directory / EXPECTED[case]).write_bytes(b'fixture')
    crt = dict(opened=opened, open_errno=0 if opened else errno.EILSEQ if case == 'invalid' else errno.EACCES,
               dos_error=0, last_error=0, acp=1252, oem=437,
               write_ok=opened, close_result=0 if opened else -1)
    output = json.dumps(crt) + '\n'
    record = dict(exit_code=0, error=None, output_origin='actual subprocess capture')
    for label, text in (('stdout', output), ('stderr', '')):
        data = text.encode()
        record[label] = dict(text=text, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), truncated=False)
    return record, output


class WindowsUnicodeDiagnosticTests(unittest.TestCase):
    def test_patch_is_exact_and_only_changes_two_source_files(self):
        patch = Path(__file__).with_name('windows_unicode_stl.patch').read_bytes()
        self.assertEqual(hashlib.sha256(patch).hexdigest(), SOURCE_PATCH_SHA256)
        names = [line.split()[2] for line in patch.decode().splitlines() if line.startswith('diff --git ')]
        self.assertEqual(sorted(names), ['a/src/geom_core/Vehicle.cpp', 'a/src/util/FileUtil.h'])
        self.assertIn('FOpenUTF8', patch.decode())
        self.assertIn('#include <system_error>', patch.decode())
        self.assertIn('catch ( const std::system_error& )', patch.decode())
        self.assertNotIn('catch ( const fs::filesystem_error& )', patch.decode())
        attributes = (Path(__file__).parents[1] / '.gitattributes').read_text()
        self.assertIn('scripts/windows_unicode_stl.patch text eol=lf', attributes)
        self.assertIn('1d6b0b6078716db5854ff04a92610aa58956a0c6', SOURCE_BASELINE)

    def test_directory_evidence_preserves_unicode_without_parent_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / STL_FILENAME).write_bytes(b'fixture')
            record = directory_records(root)[0]
            self.assertEqual(record['name'], STL_FILENAME)
            self.assertEqual(record['utf8_hex'], STL_FILENAME.encode().hex())
            self.assertEqual(record['utf16le_hex'], STL_FILENAME.encode('utf-16le').hex())
            self.assertTrue(record['exists'])
            self.assertNotIn(d, json.dumps(record))
            missing = path_record(root, 'not-present.stl')
            self.assertFalse(missing['exists'])
            self.assertIsInstance(missing['errno'], int)

    def test_actual_capture_has_real_byte_count_hash_and_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            record, raw = capture([sys.executable, '-c',
                                  'import sys; print("REAL_OUTPUT"); sys.exit(7)'], Path(d))
        self.assertEqual(record['exit_code'], 7)
        self.assertEqual(record['output_origin'], 'actual subprocess capture')
        # subprocess stdout is bytes; Python's newline convention differs by OS.
        output = b'REAL_OUTPUT\r\n' if sys.platform == 'win32' else b'REAL_OUTPUT\n'
        self.assertEqual(record['stdout']['bytes'], len(output))
        self.assertEqual(record['stdout']['sha256'], hashlib.sha256(output).hexdigest())
        self.assertIn('REAL_OUTPUT', raw)

    def test_output_is_bounded_and_known_machine_paths_are_removed(self):
        with tempfile.TemporaryDirectory() as d:
            record, _ = capture([sys.executable, '-c',
                                 'import os; print(os.getcwd()); print("x" * 20000)'], Path(d))
        self.assertTrue(record['stdout']['truncated'])
        self.assertGreater(record['stdout']['bytes'], 20000)
        self.assertNotIn(d, record['stdout']['text'])
        self.assertIn('<fixture-root>', record['stdout']['text'])
        self.assertEqual(redact('C:/fixture/file C:\\fixture\\file', ['C:\\fixture']),
                         '<fixture-root>/file <fixture-root>\\file')

    def test_redaction_precedes_truncation_at_a_path_boundary(self):
        output = b'x' * 16380 + b'C:\\private-root\\fixture.txt'
        process = subprocess.CompletedProcess('fixture', 0, stdout=output, stderr=b'')
        with mock.patch('subprocess.run', return_value=process):
            result, _ = capture(['fixture'], Path('.'), ['C:\\private-root'])
        self.assertTrue(result['stdout']['text'].endswith('<fix'))
        self.assertNotIn('C:', result['stdout']['text'])
        self.assertEqual(result['stdout']['bytes'], len(output))

    def test_capture_preserves_timeout_and_os_error_categories(self):
        with mock.patch('subprocess.run', side_effect=subprocess.TimeoutExpired('fixture', 1, output=b'partial')):
            record, _ = capture(['fixture'], Path('.'))
        self.assertEqual(record['error'], 'timeout')
        self.assertIsNone(record['exit_code'])
        self.assertEqual(record['stdout']['bytes'], 7)
        with mock.patch('subprocess.run', side_effect=FileNotFoundError(2, 'not found')):
            record, _ = capture(['fixture'], Path('.'))
        self.assertEqual(record['error']['errno'], 2)
        self.assertEqual(record['stdout']['bytes'], 0)

    def test_probe_keeps_failed_process_and_runs_remaining_cases(self):
        def capture_failure(*args):
            record, output = successful_probe_capture(*args)
            if args[0][1:] == ['narrow', 'ascii']:
                record['exit_code'] = 3221226505
                record['stderr']['text'] = 'actual crash output'
            return record, output
        with mock.patch('native_windows_unicode.capture', side_effect=capture_failure):
            report = probe(Path('probe'))
        self.assertFalse(report['passed'])
        failed = report['cases'][0]
        self.assertEqual((failed['mode'], failed['case']), ('narrow', 'ascii'))
        self.assertEqual(failed['exit_code'], 3221226505)
        self.assertEqual(failed['stderr']['text'], 'actual crash output')
        self.assertIn('process-exit', failed['transport_errors'])
        self.assertTrue(all(r['passed'] for r in report['cases'][1:]))
        self.assertEqual(report['failed_cases'][0]['exit_code'], 3221226505)
        self.assertEqual(len(report['cases']), 16 if sys.platform == 'win32' else 14)

    def test_probe_keeps_invalid_json_and_wrong_record_shape(self):
        for output, error in (('not JSON', 'invalid-json'), ('', 'invalid-json'),
                              ('[]', 'invalid-crt-record'), ('{}', 'invalid-crt-record')):
            with self.subTest(output=output):
                def malformed(*args):
                    record, _ = successful_probe_capture(*args)
                    record['stdout']['text'] = output
                    return record, output
                with mock.patch('native_windows_unicode.capture', side_effect=malformed):
                    report = probe(Path('probe'))
                self.assertFalse(report['passed'])
                self.assertTrue(all(error in r['transport_errors'] for r in report['cases']))
                self.assertTrue(all(r['exit_code'] == 0 for r in report['cases']))
                self.assertEqual(report['cases'][0]['stdout']['text'], output)

    def test_probe_keeps_exception_category_for_windows_invalid_utf8(self):
        def exception(*args):
            record, output = successful_probe_capture(*args)
            if args[0][1:] == ['utf8', 'invalid']:
                record['exit_code'] = 3
                record['stdout']['text'] = json.dumps(dict(exception='system_error', stage='open', error_code=1113))
                record['stderr']['text'] = 'CRT probe exception (open): conversion failed'
            return record, output
        with mock.patch('native_windows_unicode.codepages', return_value=dict(platform='Windows', acp=1252, oem=437)), \
                mock.patch('native_windows_unicode.capture', side_effect=exception):
            report = probe(Path('probe'))
        self.assertEqual(len(report['cases']), 16)
        self.assertFalse(report['passed'])
        failed = report['cases'][-1]
        self.assertEqual(failed['case'], 'invalid')
        self.assertEqual(failed['crt']['exception'], 'system_error')
        self.assertEqual(failed['exit_code'], 3)
        self.assertEqual(failed['transport_errors'], ['process-exit', 'invalid-crt-record'])

    def test_probe_success_and_failure_guards_are_not_weakened(self):
        with mock.patch('native_windows_unicode.codepages', return_value=dict(platform='Windows', acp=1252, oem=437)), \
                mock.patch('native_windows_unicode.capture', side_effect=successful_probe_capture):
            report = probe(Path('probe'))
        self.assertTrue(report['passed'])
        fixed = {r['case']: r for r in report['cases'] if r['mode'] == 'utf8'}
        for mutate in (
                lambda r: r['expected'].update(exists=False),
                lambda r: r['expected'].update(file=False),
                lambda r: r['expected'].update(bytes=0),
                lambda r: r['crt'].update(opened=False),
                lambda r: r['crt'].update(write_ok=False),
                lambda r: r['crt'].update(close_result=-1)):
            broken = copy.deepcopy(fixed['unicode']); mutate(broken)
            self.assertFalse(probe_case_passed(broken))
        for case in ('blocked', 'missing', 'invalid'):
            broken = copy.deepcopy(fixed[case]); broken['crt']['open_errno'] = 0
            self.assertFalse(probe_case_passed(broken))
            broken = copy.deepcopy(fixed[case]); broken['crt']['opened'] = True
            self.assertFalse(probe_case_passed(broken))
        broken = copy.deepcopy(fixed['invalid']); broken['files'].append(dict(file=True))
        self.assertFalse(probe_case_passed(broken))

    def test_crt_command_saves_failed_evidence_then_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / 'evidence' / 'crt.json'
            # Python is a real failing fixture executable: it cannot open a script
            # named "narrow" or "utf8" in each generated isolated directory.
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('native_windows_unicode.py')),
                                     'crt', '--executable', sys.executable, '--output', str(output)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(result.returncode, 1)
            report = json.loads(output.read_text())
            self.assertFalse(report['passed'])
            self.assertTrue(report['failed_cases'])
            failed = report['cases'][0]
            self.assertEqual((failed['mode'], failed['case'], failed['exit_code']), ('narrow', 'ascii', 2))
            self.assertGreater(failed['stderr']['bytes'], 0)
            self.assertIn('CRT failure:', result.stdout.decode())

    def test_comparison_requires_actual_mojibake_directory_entry(self):
        old, new = reports()
        self.assertTrue(compare(old, new)['patched_all_gates_passed'])
        for mutate in (
                lambda r: r['cases'][1].update(files=[]),
                lambda r: r['cases'][1]['files'][0].update(name=STL_FILENAME),
                lambda r: r['cases'][1]['files'][0].update(bytes=0),
                lambda r: r['cases'][1].update(exit_code=1),
                lambda r: r['cases'][1].update(markers_passed=False),
                lambda r: r['cases'][1].update(disk_error='other'),
                lambda r: r['cases'][1]['expected'].update(exists=True),
                lambda r: r['cases'][1]['stdout'].update(bytes=0),
                lambda r: r['cases'][0].update(passed=False),
                lambda r: r['environment'].update(acp=65001)):
            broken = copy.deepcopy(old); mutate(broken)
            with self.assertRaises(ValueError): compare(broken, new)

    def test_comparison_rejects_missing_patched_gates_and_same_executable(self):
        old, new = reports()
        new['passed'] = False
        with self.assertRaises(ValueError): compare(old, new)
        new['passed'] = True; new['executable_sha256'] = old['executable_sha256']
        with self.assertRaises(ValueError): compare(old, new)

    def test_apply_creates_only_clean_local_diagnostic_child(self):
        tooling = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            source = Path(d)
            subprocess.run(['git', 'init', '-q', str(source)], check=True)
            for name in ('src/geom_core/Vehicle.cpp', 'src/util/FileUtil.h'):
                content = (tooling / name).read_bytes()
                path = source / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(content)
            subprocess.run(['git', '-C', d, 'apply', '--reverse', str(tooling / 'scripts/windows_unicode_stl.patch')], check=True)
            subprocess.run(['git', '-C', d, 'add', '.'], check=True)
            subprocess.run(['git', '-C', d, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                            'commit', '-qm', 'fixture baseline'], check=True)
            before = subprocess.check_output(['git', '-C', d, 'rev-parse', 'HEAD'], text=True).strip()
            with mock.patch('native_windows_unicode.SOURCE_BASELINE', before):
                result = apply_patch(source, tooling)
            self.assertEqual(result['temporary_parent'], before)
            self.assertNotEqual(result['temporary_source_sha'], before)
            self.assertTrue(result['diagnostic_only'])
            self.assertFalse(result['promotion_eligible'])
            self.assertEqual(subprocess.check_output(['git', '-C', d, 'status', '--porcelain']), b'')
            self.assertEqual(subprocess.check_output(['git', '-C', d, 'remote']), b'')
            changed = subprocess.check_output(['git', '-C', d, 'diff', '--name-only', before], text=True).splitlines()
            self.assertEqual(changed, result['changed_files'])

    def test_full_production_gates_follow_temporary_commit_without_dirty_override(self):
        script = Path(__file__).with_name('native_windows_unicode.ps1').read_text()
        self.assertIn('$env:BACKFILL_SHA = $patch.temporary_source_sha', script)
        self.assertIn('native_verify.py O:\\patched-stage O:\\source O:\\diagnostic-deliverables', script)
        self.assertIn("throw 'Patched complete production verification failed'", script)
        self.assertNotIn('allow-dirty', script)
        self.assertNotIn('git push', script)
        workflow = (Path(__file__).parents[1] / '.github/workflows/windows-unicode-diagnostic.yml').read_text()
        self.assertNotIn('diagnostic-deliverables/*', workflow)
        self.assertIn('path: unicode-evidence/*.json', workflow)

    def test_workflow_is_single_family_read_only_and_does_not_publish(self):
        text = (Path(__file__).parents[1] / '.github/workflows/windows-unicode-diagnostic.yml').read_text()
        self.assertIn('pull_request:', text)
        self.assertIn("'src/geom_core/Vehicle.cpp'", text)
        self.assertIn('contents: read', text)
        self.assertIn('runs-on: windows-2022', text)
        self.assertIn(SOURCE_BASELINE, text)
        self.assertNotIn('matrix:', text)
        self.assertNotIn('secrets.', text)
        self.assertNotIn('contents: write', text)
        self.assertNotIn('native_release.py', text)
        self.assertNotIn('native_promote.py', text)


if __name__ == '__main__': unittest.main()
