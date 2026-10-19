#!/usr/bin/env python3
"""Exercise candidate identity without mutating source or contacting a release service."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import check_localization_release as release_guard

ROOT = Path(__file__).resolve().parents[1]
VERSION_SOURCE = (ROOT / 'src/cmake/VSP_Version.cmake').read_text(encoding='utf-8')
VERSION = '.'.join(re.search(rf'SET\(\s*VSPVER_{key}\s+(\d+)\s*\)', VERSION_SOURCE)[1]
                   for key in ('MAJOR', 'MINOR', 'PATCH'))
ABOUT_SOURCE = (ROOT / 'src/gui_and_draw/MainVSPScreen.cpp').read_text(encoding='utf-8')
CANDIDATE = re.search(r'汉化版本：(\d+\.\d+\.\d+-zh-CN\.rc\.[1-9]\d*)\\n', ABOUT_SOURCE)[1]

class CandidateIdentityTests(unittest.TestCase):
    def run_guard(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/check_localization_release.py'), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def test_exact_candidate_passes(self):
        result = self.run_guard('--expected-tag', CANDIDATE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_version_report_matches_source(self):
        result = self.run_guard('--print-version')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), VERSION)

    def test_readme_current_identity_matches_candidate(self):
        readme = (ROOT / 'README_zh-CN.md').read_text(encoding='utf-8')
        self.assertIn('当前汉化版本：`' + CANDIDATE + '`', readme)

    def test_current_display_copy_is_tool_neutral(self):
        for name in ('src/gui_and_draw/MainVSPScreen.cpp', 'src/gui_and_draw/VSPChinese.cpp',
                     'src/help/index.md', 'src/help/html/index.html'):
            with self.subTest(source=name):
                self.assertNotIn('Codex', (ROOT / name).read_text(encoding='utf-8'))

    def test_other_version_is_rejected(self):
        self.assertNotEqual(self.run_guard('--expected-tag', '99.99.99-zh-CN.rc.1').returncode, 0)

    def test_other_revision_is_rejected(self):
        self.assertNotEqual(self.run_guard('--expected-tag', VERSION + '-zh-CN.rc.' + str(int(CANDIDATE.rsplit('.', 1)[1]) + 1)).returncode, 0)

    def test_current_source_cannot_impersonate_historical_release(self):
        self.assertNotEqual(self.run_guard('--expected-tag', VERSION + '-Codex-AI-zh-CN').returncode, 0)

    def test_zero_revision_is_rejected(self):
        self.assertNotEqual(self.run_guard('--expected-tag', VERSION + '-zh-CN.rc.0').returncode, 0)


class BundledModelDataTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.examples = self.root / 'examples/Complete_Aircraft'
        self.examples.mkdir(parents=True)

    def write_model(self, names):
        root = ET.Element('Vsp_Geometry')
        vehicle = ET.SubElement(root, 'Vehicle')
        for name in names:
            geom = ET.SubElement(vehicle, 'Geom')
            container = ET.SubElement(geom, 'ParmContainer')
            if name is not None:
                ET.SubElement(container, 'Name').text = name
            ET.SubElement(geom, 'Geom')  # Implementation node must not need a name.
        path = self.examples / 'model.vsp3'
        path.write_bytes(ET.tostring(root, encoding='utf-8', xml_declaration=True))
        return path

    def check_models(self):
        with patch.object(release_guard, 'ROOT', self.root):
            return release_guard.verify_bundled_model_data()

    def test_opaque_names_do_not_need_translations_or_change_file_bytes(self):
        names = ['Wing', 'Export', 'Cancel', '机翼', '取消', 'Wing&Body',
                 'Wing &amp; Body', '<Wing> / "Left"', '  用户名称  ', 'Wing']
        path = self.write_model(names)
        original = path.read_bytes()
        self.assertEqual(self.check_models(), (1, len(names)))
        self.assertEqual(path.read_bytes(), original)

    def test_empty_name_is_valid_model_data(self):
        path = self.write_model([''])
        original = path.read_bytes()
        self.assertEqual(self.check_models(), (1, 1))
        self.assertEqual(path.read_bytes(), original)

    def test_missing_name_is_rejected(self):
        self.write_model([None])
        with self.assertRaisesRegex(SystemExit, '纯文本名称'):
            self.check_models()

    def test_markup_inside_name_is_rejected(self):
        path = self.write_model(['Wing'])
        path.write_bytes(path.read_bytes().replace(b'<Name>Wing</Name>', b'<Name><Wing/></Name>'))
        with self.assertRaisesRegex(SystemExit, '纯文本名称'):
            self.check_models()

    def test_malformed_xml_is_rejected(self):
        (self.examples / 'broken.vsp3').write_text('<Vsp_Geometry>')
        with self.assertRaisesRegex(SystemExit, 'XML 不可读'):
            self.check_models()

    def test_model_without_geometry_is_rejected(self):
        self.write_model([])
        with self.assertRaisesRegex(SystemExit, '缺少几何体'):
            self.check_models()

    def test_missing_bundled_models_is_rejected(self):
        with self.assertRaisesRegex(SystemExit, '整机案例缺失'):
            self.check_models()


if __name__ == '__main__':
    unittest.main()
