"""Offline contracts for the single-family generated-fixture diagnosis."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from native_windows_unicode import (SOURCE_BASELINE, SOURCE_PATCH_SHA256, STL_FILENAME, apply_patch,
                                    capture, compare, directory_records, path_record, redact)


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


class WindowsUnicodeDiagnosticTests(unittest.TestCase):
    def test_patch_is_exact_and_only_changes_two_source_files(self):
        patch = Path(__file__).with_name('windows_unicode_stl.patch').read_bytes()
        self.assertEqual(hashlib.sha256(patch).hexdigest(), SOURCE_PATCH_SHA256)
        names = [line.split()[2] for line in patch.decode().splitlines() if line.startswith('diff --git ')]
        self.assertEqual(sorted(names), ['a/src/geom_core/Vehicle.cpp', 'a/src/util/FileUtil.h'])
        self.assertIn('FOpenUTF8', patch.decode())
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
        self.assertIn('contents: read', text)
        self.assertIn('runs-on: windows-2022', text)
        self.assertIn(SOURCE_BASELINE, text)
        self.assertNotIn('matrix:', text)
        self.assertNotIn('secrets.', text)
        self.assertNotIn('contents: write', text)
        self.assertNotIn('native_release.py', text)
        self.assertNotIn('native_promote.py', text)


if __name__ == '__main__': unittest.main()
