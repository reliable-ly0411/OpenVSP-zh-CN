"""Source contracts for material action labels and opaque material names.

Together with material_label_context.cpp these are focused source/unit checks;
they do not substitute for displaying and inspecting the native FLTK GUI.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / 'src/gui_and_draw'


class MaterialLabelContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.screen = (GUI / 'ScreenBase.cpp').read_text(encoding='utf-8')
        cls.custom = (GUI / 'CustomScreen.cpp').read_text(encoding='utf-8')
        cls.device = (GUI / 'GuiDevice.cpp').read_text(encoding='utf-8')
        cls.header = (GUI / 'GuiDevice.h').read_text(encoding='utf-8')

    def test_material_button_uses_its_own_fixed_context(self):
        labels = re.findall(r'AddButton\(\s*m_CustomMaterialButton\s*,\s*"([^"]+)"\s*\)', self.screen)
        self.assertEqual(labels, ['Customize Material'])
        self.assertRegex(self.custom, r'CustomScreen::CustomScreen\([^\n]+GeomScreen\([^\n]+"Custom"\s*\)')

    def test_material_names_are_passed_raw_without_translation(self):
        body = self.screen.split('void GeomScreen::UpdateMaterialNames()', 1)[1].split(
            'void GeomScreen::GuiDeviceCallBack(', 1)[0]
        self.assertIn('matNames = MaterialMgr.GetNames();', body)
        self.assertRegex(body, r'm_MaterialChoice\.AddItemRaw\(\s*matNames\[i\]\s*\)')
        self.assertNotRegex(body, r'\bVSPTranslate\w*\s*\(')
        self.assertNotRegex(body, r'AddItem\(\s*matNames\[i\]')

    def test_original_custom_material_name_and_selection_are_unchanged(self):
        callback = self.screen.split('void GeomScreen::GuiDeviceCallBack(', 1)[1]
        custom = callback.split('else if ( device == &m_CustomMaterialButton )', 1)[1].split(
            'else if ( device == &m_ScaleAcceptButton )', 1)[0]
        self.assertIn('geom_ptr->GetMaterial()->m_Name = "Custom";', custom)
        self.assertNotRegex(custom, r'\bVSPTranslate\w*\s*\(')
        self.assertIn('geom_ptr->SetMaterial( mat.m_Name, mat.m_Ambi, mat.m_Diff, mat.m_Spec, mat.m_Emis, mat.m_Shininess );', callback)

    def test_choice_raw_flag_bypasses_catalog_for_same_named_values(self):
        choice = self.header.split('class Choice : public GuiDevice', 1)[1].split('\n};', 1)[0]
        raw = re.findall(r'void AddItemRaw\([^)]*\)\s*\{([^}]+)\}', choice)
        self.assertEqual(len(raw), 2)
        for body in raw:
            self.assertRegex(body, r'AddItem\(\s*item(?:,\s*val)?\s*\)')
            self.assertIn('m_RawItems.back() = true;', body)
        ordinary = re.findall(r'void AddItem\([^)]*\)\s*\{([^}]+)\}', choice)
        self.assertEqual(len(ordinary), 2)
        for body in ordinary:
            self.assertIn('m_Items.push_back( item );', body)
        update = self.device.split('void Choice::UpdateItems(', 1)[1].split('//==== CallBack ====', 1)[0]
        self.assertIn('const string label = m_RawItems[i] ? m_Items[i] : VSPTranslate( m_Items[i] );', update)
        self.assertIn('m_Choice->replace( i, label.c_str() );', update)


if __name__ == '__main__':
    unittest.main()
