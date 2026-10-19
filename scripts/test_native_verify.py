"""Portable unit coverage for platform inspection; no generated binaries execute."""
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

from backfill_verify import audit_native
from native_verify import audit_windows


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
