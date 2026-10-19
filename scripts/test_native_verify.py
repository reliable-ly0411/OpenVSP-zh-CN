"""Portable unit coverage for platform inspection; no generated binaries execute."""
import os
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from backfill_verify import audit_native
from native_verify import (BOUNDARY_MODEL_FILENAME, BOUNDARY_MODEL_NAMES,
                           audit_windows, run_script_smoke, smoke_failure_report, smoke_script_path,
                           verify_boundary_output)


class ScriptDiagnosticsTests(unittest.TestCase):
    def execute(self, root, **mock):
        with patch('native_verify.run', **mock):
            return run_script_smoke(root / 'vspscript', root / 'localization_boundary_smoke.as',
                                    root, {'HOME': 'private-home'}, root / 'diagnostics')

    def test_success_does_not_create_failure_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.execute(root, return_value='LOCALIZATION_BOUNDARIES_PASS')
            self.assertFalse((root / 'diagnostics').exists())

    def test_nonzero_preserves_value_free_compiler_diagnosis(self):
        private = "/private/person/model.as (26, 53) : ERR : No matching symbol 'FindGeomsWithName'\nsecret-value"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            error = subprocess.CalledProcessError(1, ['/private/person/vspscript'], output=private)
            with self.assertRaisesRegex(ValueError, 'angelscript-compile-error') as caught:
                self.execute(root, side_effect=error)
            data = (root / 'diagnostics/runtime.json').read_text()
            report = json.loads(data)
            self.assertEqual(report['exit_code'], 1)
            self.assertEqual(report['compile_locations'], [{'row': 26, 'column': 53}])
            self.assertEqual(report['known_missing_symbols'], ['FindGeomsWithName'])
            self.assertFalse(report['contains_output_values'])
            self.assertFalse(report['binary_uploaded'])
            for value in ('private/person', 'secret-value'):
                self.assertNotIn(value, data + str(caught.exception))
            self.assertIsNone(caught.exception.__cause__)

    def test_arbitrary_missing_symbols_and_values_are_not_copied(self):
        text = "a (3, 4) : ERR : No matching symbol 'private_user_name'\npassword=private-secret"
        result = smoke_failure_report(text, 'localization_boundary_smoke.as', 1)
        self.assertEqual(result['known_missing_symbols'], [])
        self.assertNotIn('private', json.dumps(result))

    def test_failure_or_absent_marker_fails_even_with_zero_exit(self):
        for output, category in (('LOCALIZATION_BOUNDARIES_FAIL', 'script-reported-failure'),
                                 ('LOCALIZATION_BOUNDARIES_PASS LOCALIZATION_BOUNDARIES_FAIL', 'script-reported-failure'),
                                 ('unclassified output', 'missing-success-marker')):
            with self.subTest(output=output), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                with self.assertRaisesRegex(ValueError, category):
                    self.execute(root, return_value=output)
                self.assertEqual(json.loads((root / 'diagnostics/runtime.json').read_text())['exit_code'], 0)

    def test_success_marker_does_not_hide_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(ValueError, 'process-nonzero-exit'):
            self.execute(Path(temp), side_effect=subprocess.CalledProcessError(
                2, ['vspscript'], output='LOCALIZATION_BOUNDARIES_PASS'))

    def test_timeout_bytes_and_unavailable_launcher_remain_failures(self):
        for error, category in ((subprocess.TimeoutExpired(['private-path'], 120, output=b'private-output'), 'timeout'),
                                 (FileNotFoundError('private-path'), 'launcher-unavailable')):
            with self.subTest(category=category), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                with self.assertRaisesRegex(ValueError, category): self.execute(root, side_effect=error)
                self.assertNotIn('private-', (root / 'diagnostics/runtime.json').read_text())

    def test_unknown_script_is_rejected_without_invocation(self):
        with patch('native_verify.run') as run, self.assertRaisesRegex(ValueError, 'Unknown'):
            run_script_smoke(Path('vspscript'), Path('private.as'), Path('.'), {}, Path('.'))
        run.assert_not_called()


class SmokeOriginTests(unittest.TestCase):
    def test_common_tooling_script_executes_when_old_source_has_no_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source'; (source / 'scripts').mkdir(parents=True)
            tooling = root / 'tooling'; tooling.mkdir()
            baseline = tooling / 'backfill_smoke.as'; baseline.write_text('baseline fixture')
            selected = smoke_script_path('backfill_smoke.as', source, tooling)
            self.assertEqual(selected, baseline)
            self.assertFalse((source / 'scripts/backfill_smoke.as').exists())
            with patch('native_verify.run', return_value='LOCALIZATION_SMOKE_PASS') as run:
                run_script_smoke(root / 'vspscript', selected, root, {}, root / 'diagnostics')
            self.assertEqual(run.call_args.args[2], baseline)

    def test_missing_tooling_baseline_fails_even_when_source_has_a_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); source = root / 'source'; (source / 'scripts').mkdir(parents=True)
            (source / 'scripts/backfill_smoke.as').write_text('source fixture')
            with self.assertRaisesRegex(ValueError, 'Missing mandatory tooling'):
                smoke_script_path('backfill_smoke.as', source, root / 'tooling')

    def test_family_checks_require_exact_source_and_never_fall_back_to_tooling(self):
        for name in ('localization_boundary_smoke.as', 'localization_resources_smoke.as'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp); source = root / 'source'; (source / 'scripts').mkdir(parents=True)
                tooling = root / 'tooling'; tooling.mkdir(); (tooling / name).write_text('wrong fixture')
                with self.assertRaisesRegex(ValueError, 'Missing mandatory source'):
                    smoke_script_path(name, source, tooling)
                expected = source / 'scripts' / name; expected.write_text('source fixture')
                self.assertEqual(smoke_script_path(name, source, tooling), expected)


class FilesystemBoundaryTests(unittest.TestCase):
    def write_model(self, directory, names=BOUNDARY_MODEL_NAMES, filename=BOUNDARY_MODEL_FILENAME):
        root = ET.Element('Vsp_Geometry')
        vehicle = ET.SubElement(root, 'Vehicle')
        for name in names:
            geom = ET.SubElement(vehicle, 'Geom')
            container = ET.SubElement(geom, 'ParmContainer')
            ET.SubElement(container, 'Name').text = name
        path = Path(directory) / filename
        ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)
        return path

    def test_unicode_filename_and_all_persisted_names_are_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.write_model(temp)
            before = path.read_bytes()
            result = verify_boundary_output(temp)
            self.assertEqual(result['persisted_names'], 14)
            self.assertEqual(path.read_bytes(), before)
            self.assertIn(b'&amp;amp;', before)

    def test_slash_request_uses_upstream_accepted_name_without_weakening_other_names(self):
        self.assertEqual(BOUNDARY_MODEL_NAMES[11], 'Wing  Fuselage: Export_100%')
        requested = list(BOUNDARY_MODEL_NAMES)
        requested[11] = 'Wing / Fuselage: Export_100%'
        with tempfile.TemporaryDirectory() as temp:
            self.write_model(temp, names=requested)
            with self.assertRaisesRegex(ValueError, 'Persisted model names'):
                verify_boundary_output(temp)

    def test_lossy_filename_is_not_accepted_as_a_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            self.write_model(temp, filename='Wing Design 100% ??.vsp3')
            with self.assertRaisesRegex(ValueError, 'Unicode filename'):
                verify_boundary_output(temp)

    def test_rewritten_missing_or_duplicate_names_fail(self):
        for names in (['机翼'] + list(BOUNDARY_MODEL_NAMES[1:]),
                      BOUNDARY_MODEL_NAMES[:-1], BOUNDARY_MODEL_NAMES + ('Wing',)):
            with self.subTest(names=names), tempfile.TemporaryDirectory() as temp:
                self.write_model(temp, names=names)
                with self.assertRaisesRegex(ValueError, 'Persisted model names'):
                    verify_boundary_output(temp)

    def test_malformed_xml_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / BOUNDARY_MODEL_FILENAME).write_text('<broken>', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'not valid XML'):
                verify_boundary_output(temp)


class NativeInspectionTests(unittest.TestCase):
    def test_elf_audit_accepts_exact_amd64_and_rejects_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ('vsp', 'vspscript', 'vspaero', 'vspviewer', 'vsploads', '_vsp.so'):
                (root / name).write_bytes(b'inert fixture')
            def command(*args, **kwargs):
                if args[0] == 'file': return 'ELF 64-bit'
                if args[:2] == ('readelf', '-h'): return 'Machine: Advanced Micro Devices X86-64\n'
                if args[:2] == ('readelf', '-d'): return ''
                if args[0] == 'ldd': return ''
                raise AssertionError(args)
            with patch('backfill_verify.run', side_effect=command):
                self.assertEqual(len(audit_native(root, 'x86_64', False)), 6)
                with self.assertRaises(ValueError): audit_native(root, 'aarch64', False)
                with self.assertRaises(ValueError): audit_native(root, 'unknown', False)

    def test_windows_pe_machine_imports_and_python_extension_are_required(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'package'; root.mkdir()
            system = Path(temp) / 'Windows'; (system / 'System32').mkdir(parents=True)
            (system / 'System32/kernel32.dll').write_bytes(b'system fixture')
            for name in ('vsp', 'vspscript', 'vspaero', 'vspviewer', 'vsploads'):
                (root / (name + '.exe')).write_bytes(b'inert fixture')
            (root / '_vsp.pyd').write_bytes(b'inert fixture')
            machine = 0x8664
            library = b'kernel32.dll'
            def pe(*args, **kwargs):
                return SimpleNamespace(FILE_HEADER=SimpleNamespace(Machine=machine),
                                       parse_data_directories=lambda **kwargs: None, close=lambda: None,
                                       DIRECTORY_ENTRY_IMPORT=[SimpleNamespace(dll=library)])
            module = SimpleNamespace(PE=pe, DIRECTORY_ENTRY={'IMAGE_DIRECTORY_ENTRY_IMPORT':1,'IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT':13})
            with patch.dict(sys.modules, {'pefile':module}), patch.dict(os.environ, {'SystemRoot':str(system)}):
                self.assertEqual(len(audit_windows(root, 'x86_64')), 6)
                machine = 0xAA64
                with self.assertRaises(ValueError): audit_windows(root, 'x86_64')
                machine = 0x8664; library = b'missing-private.dll'
                with self.assertRaises(ValueError): audit_windows(root, 'x86_64')
                with self.assertRaises(ValueError): audit_windows(root, 'arm64')


if __name__ == '__main__':
    unittest.main()
