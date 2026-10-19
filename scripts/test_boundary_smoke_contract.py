"""Keep the native smoke aligned with the official API's accepted-name contract.

These source checks do not replace executing the AngelScript on each native package.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BoundarySmokeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.smoke = (ROOT / 'scripts/localization_boundary_smoke.as').read_text(encoding='utf-8')

    def test_fourteen_exact_accepted_names(self):
        match = re.search(r'array<string> names\s*=\s*\{(.*?)\};', self.smoke, re.S)
        self.assertIsNotNone(match)
        names = json.loads('[' + match[1] + ']')
        self.assertEqual(names, [
            'Wing', 'Fuselage', 'CG', 'Pod_3', '主翼', '用户模型_7',
            'Export', 'Cancel', '机翼', '取消', 'Wing &amp; Body',
            'Wing  Fuselage: Export_100%', '@b@.Wing|Left:Right', 'Wing&Body_1',
        ])
        self.assertEqual(len(set(names)), 14)

    def test_slash_request_is_checked_before_and_after_save(self):
        self.assertIn('if (i == 11) requested_name = "Wing / Fuselage: Export_100%";', self.smoke)
        self.assertIn('SetGeomName(id, requested_name);', self.smoke)
        immediate = self.smoke.index('if (GetGeomName(id) != names[i])')
        self.assertLess(immediate, self.smoke.index('WriteVSPFile(filename, SET_ALL);'))
        self.assertIn('if (GetGeomName(ids[i]) != names[i])', self.smoke)
        self.assertIn('FindGeomsWithName(names[i])', self.smoke)

    def test_official_slash_normalization_is_preserved(self):
        implementation = (ROOT / 'src/geom_core/ParmContainer.cpp').read_text(encoding='utf-8')
        declaration = (ROOT / 'src/geom_core/ParmContainer.h').read_text(encoding='utf-8')
        self.assertIn("StringUtil::remove_all( temp_name, '/' );", implementation)
        self.assertRegex(declaration, r'SetName\([^;]*removeslashes\s*=\s*true')

    def test_unicode_filename_and_failure_categories_remain_explicit(self):
        self.assertIn('string filename = "Wing Design 100% 中文.vsp3";', self.smoke)
        self.assertIn('ReadVSPFile(filename);', self.smoke)
        for category in ('set_name', 'count', 'reloaded_name', 'lookup', 'parameter', 'api_error'):
            self.assertIn('Print("LOCALIZATION_BOUNDARIES_FAIL:' + category + '");', self.smoke)
        self.assertIn('Print("LOCALIZATION_BOUNDARIES_PASS");', self.smoke)
        self.assertNotIn('Print(GetGeomName', self.smoke)
        self.assertNotIn('Print(filename)', self.smoke)


if __name__ == '__main__':
    unittest.main()
