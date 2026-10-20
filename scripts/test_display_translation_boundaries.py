#!/usr/bin/env python3
"""Check GUI call sites as well as catalog strings for display/data boundaries.

These source contracts complement the real VSPChinese C++ tests. They are not
native GUI execution or visual acceptance tests.
"""
from pathlib import Path
import re
import unittest

from check_translation_catalog import has_unconditional_translation_include, strip_comments

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / 'src/gui_and_draw'


def export_alert_is_safe(source):
    """The format is translated before opaque values reach FLTK's formatter."""
    return bool(re.search(
        r'\bfl_alert\s*\(\s*VSPTranslateMessage\s*\(\s*"%s, %s not written"\s*\)'
        r'\s*\.c_str\(\s*\)\s*,\s*err\.c_str\(\s*\)\s*,\s*newfile\.c_str\(\s*\)\s*\)',
        strip_comments(source)))


def parm_title_is_safe(source):
    return bool(re.search(
        r'\bSetTitleRaw\s*\(\s*VSPTranslateLabelAndValue\s*\(\s*"Parm: "\s*,\s*'
        r'parm_ptr->GetName\(\s*\)\s*\)\s*\)', strip_comments(source)))


class DisplayTranslationBoundaryTests(unittest.TestCase):
    def test_export_alert_translates_template_before_formatting(self):
        source = (GUI / 'ExportScreen.cpp').read_text(encoding='utf-8')
        if 'SplitStitchSurfaces' not in strip_comments(source):
            self.skipTest('This upstream version has no split/stitch export alert')
        self.assertTrue(export_alert_is_safe(source))
        self.assertTrue(has_unconditional_translation_include(source))

    def test_export_alert_guard_rejects_dead_catalog_entry(self):
        unsafe = 'fl_alert("%s, %s not written", err.c_str(), newfile.c_str());'
        self.assertFalse(export_alert_is_safe(unsafe))
        safe = ('fl_alert(VSPTranslateMessage("%s, %s not written").c_str(), '
                'err.c_str(), newfile.c_str());')
        self.assertTrue(export_alert_is_safe(safe))
        self.assertFalse(export_alert_is_safe('// ' + safe))
        self.assertFalse(export_alert_is_safe(safe.replace('VSPTranslateMessage', 'VSPTranslate')))

    def test_parameter_title_preserves_names_without_a_second_translation(self):
        source = (GUI / 'ParmScreen.cpp').read_text(encoding='utf-8')
        self.assertTrue(parm_title_is_safe(source))
        screen = (GUI / 'ScreenBase.cpp').read_text(encoding='utf-8')
        raw = screen.split('void BasicScreen::SetTitleRaw(', 1)[1].split('\n}', 1)[0]
        self.assertRegex(raw, r'copy_label\(\s*title\.c_str\(\s*\)\s*\)')
        self.assertNotRegex(strip_comments(raw), r'\bVSPTranslate\w*\s*\(')

    def test_parameter_title_guard_rejects_translating_user_names(self):
        safe = 'SetTitleRaw(VSPTranslateLabelAndValue("Parm: ", parm_ptr->GetName()));'
        self.assertTrue(parm_title_is_safe(safe))
        self.assertFalse(parm_title_is_safe(safe.replace('SetTitleRaw', 'SetTitle')))
        self.assertFalse(parm_title_is_safe('SetTitle("Parm: " + parm_ptr->GetName());'))
        self.assertFalse(parm_title_is_safe('/* ' + safe + ' */'))


if __name__ == '__main__':
    unittest.main()
