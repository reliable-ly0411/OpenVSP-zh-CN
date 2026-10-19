"""Portable unit coverage for platform inspection; no generated binaries execute."""
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from backfill_verify import audit_native
from native_verify import (BOUNDARY_MODEL_FILENAME, BOUNDARY_MODEL_NAMES,
                           audit_windows, verify_boundary_output)


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
