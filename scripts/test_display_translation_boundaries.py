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


def file_chooser_title_is_safe(source):
    return bool(re.search(
        r'\bSetTitleRaw\s*\(\s*VSPTranslateLabelAndValue\s*\(\s*title\s*,\s*filter_str\s*\)\s*\)',
        strip_comments(source)))


def attribute_title_is_safe(source):
    code = strip_comments(source)
    return all(re.search(pattern, code) for pattern in (
        r'header_str\s*=\s*VSPTranslate\(\s*"Attribute Explorer"\s*\)',
        r'header_str\s*=\s*VSPTranslateLabelAndValue\(\s*"Attribute Explorer: "\s*,\s*'
        r'AttributeMgr\.GetName\(\s*ac_ptr->GetAttachID\(\s*\)\s*\)\s*\)',
        r'\bSetTitleRaw\(\s*header_str\s*\)',
    ))


def parm_description_is_safe(source):
    code = strip_comments(source)
    # 3.51.x already displays every description raw. Do not require it to add
    # translation or a newer distinction just to satisfy this regression test.
    if re.search(r'm_DescString\.Update\(\s*parm_ptr->GetDescript\(\s*\)\s*\)', code):
        return True
    return bool(re.search(
        r'const string description\s*=\s*LinkMgr\.GetUserParmIndex\(\s*pid\s*\)\s*>=\s*0\s*\?\s*'
        r'parm_ptr->GetDescript\(\s*\)\s*:\s*VSPTranslate\(\s*parm_ptr->GetDescript\(\s*\)\s*\)\s*;\s*'
        r'm_DescString\.Update\(\s*description\s*\)', code))


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

    def test_file_chooser_composes_title_and_filter_without_retranslation(self):
        source = (GUI / 'SelectFileScreen.cpp').read_text(encoding='utf-8')
        self.assertTrue(file_chooser_title_is_safe(source))
        self.assertRegex(source, r'snprintf\(\s*filter_str,\s*sizeof\(\s*filter_str\s*\),\s*'
                                r'"   \(%s\)",\s*filter\.c_str\(\s*\)\s*\)')

    def test_file_chooser_title_guard_rejects_merged_or_double_translation(self):
        safe = 'SetTitleRaw(VSPTranslateLabelAndValue(title, filter_str));'
        self.assertTrue(file_chooser_title_is_safe(safe))
        self.assertFalse(file_chooser_title_is_safe(safe.replace('SetTitleRaw', 'SetTitle')))
        self.assertFalse(file_chooser_title_is_safe('SetTitle(title + filter_str);'))
        self.assertFalse(file_chooser_title_is_safe('SetTitleRaw(VSPTranslate(title + filter_str));'))
        self.assertFalse(file_chooser_title_is_safe('/* ' + safe + ' */'))

    def test_native_chooser_translates_only_title_and_preserves_filesystem_values(self):
        source = (GUI / 'ScreenMgr.cpp').read_text(encoding='utf-8')
        if 'string ScreenMgr::NativeFileChooser(' not in source:
            self.skipTest('This upstream version has no native file chooser')
        native = source.split('string ScreenMgr::NativeFileChooser(', 1)[1].split(
            '//==== Create Message', 1)[0]
        self.assertRegex(native, r'translated_title\s*=\s*VSPTranslate\(\s*title\s*\)')
        self.assertRegex(native, r'title\(\s*translated_title\.c_str\(\s*\)\s*\)')
        for method, value in [('filter', 'filter'), ('directory', 'dir'), ('preset_file', 'preset_fname')]:
            self.assertRegex(native, rf'->{method}\(\s*{value}\.c_str\(\s*\)\s*\)')
        self.assertEqual(re.findall(r'\bVSPTranslate\w*\(\s*([^)]*)\s*\)', strip_comments(native)), ['title '])

    def test_attribute_title_preserves_attached_geometry_or_collection_name(self):
        source = (GUI / 'AttributeScreen.cpp').read_text(encoding='utf-8')
        body = source.split('void AttributeExplorer::AttrTypeDispGroup(', 1)[1]
        self.assertTrue(attribute_title_is_safe(body))
        self.assertTrue(has_unconditional_translation_include(source))
        self.assertFalse(attribute_title_is_safe(body.replace('SetTitleRaw', 'SetTitle')))
        self.assertFalse(attribute_title_is_safe(body.replace('VSPTranslateLabelAndValue', 'VSPTranslate')))

    def test_user_description_is_opaque_and_builtin_description_remains_translatable(self):
        source = (GUI / 'ParmScreen.cpp').read_text(encoding='utf-8')
        self.assertTrue(parm_description_is_safe(source))
        self.assertFalse(parm_description_is_safe('m_DescString.Update(VSPTranslate(parm_ptr->GetDescript()));'))
        self.assertTrue(parm_description_is_safe('m_DescString.Update(parm_ptr->GetDescript());'))
        unsafe = source.replace('GetUserParmIndex( pid ) >= 0', 'GetUserParmIndex( pid ) < 0')
        if 'const string description' in source:
            self.assertFalse(parm_description_is_safe(unsafe))
        device = (GUI / 'GuiDevice.cpp').read_text(encoding='utf-8')
        raw = device.split('void StringOutput::Update(', 1)[1].split('\n}', 1)[0]
        self.assertRegex(raw, r'm_String\s*=\s*val\s*;')
        self.assertRegex(raw, r'm_Output->value\(\s*m_String\.c_str\(\s*\)\s*\)')
        self.assertNotRegex(strip_comments(raw), r'\bVSPTranslate\w*\s*\(')


if __name__ == '__main__':
    unittest.main()
