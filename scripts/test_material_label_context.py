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
        self.assertRegex(self.custom, r'CustomScreen::CustomScreen\([^\n]+GeomScreen\([^\n]+"Custom"\s*,\s*"Custom\.html"\s*\)')

    def test_both_pickers_keep_raw_names_and_gate_localization_on_provenance(self):
        mult = (GUI / 'MultTransScreen.cpp').read_text(encoding='utf-8')
        for screen, cls in [(self.screen, 'GeomScreen'), (mult, 'MultTransScreen')]:
            self.assertRegex(screen, rf'void {cls}::UpdateMaterialNames\(\)\s*{{\s*'
                             r'PopulateRenderingMaterialChoice\( m_MaterialChoice \);')
            self.assertIn('m_MaterialChoice.GetItems()', screen)
        body = self.screen.split('void PopulateRenderingMaterialChoice(', 1)[1].split(
            'void GeomScreen::UpdateMaterialNames()', 1)[0]
        self.assertIn('const auto names = MaterialMgr.GetNames();', body)
        self.assertRegex(body, r'FindMaterial\( i, mat \) && !mat\.m_UserMaterial')
        self.assertIn('choice.AddItemWithDisplayLabel( names[i], VSPTranslateMaterialPreset( names[i] ) );', body)
        self.assertIn('choice.AddItemRaw( names[i] );', body)

    def test_rendering_caption_catalog_matches_every_registered_preset(self):
        mgr = (ROOT / 'src/geom_core/MaterialMgr.cpp').read_text(encoding='utf-8')
        ctor = mgr.split('MaterialMgrSingleton::MaterialMgrSingleton()', 1)[1].split(
            'MaterialMgrSingleton::~MaterialMgrSingleton()', 1)[0]
        existing = re.findall(r'^    mat\.m_Name = +"([^"]+)";', ctor, re.M)
        labels = (GUI / 'VSPChinese.cpp').read_text(encoding='utf-8').split(
            'std::string VSPTranslateMaterialPreset(', 1)[1].split('};', 1)[0]
        self.assertEqual(re.findall(r'{ "([^"]+)",', labels), existing)
        self.assertEqual(len(existing), 36)

    def test_original_custom_material_name_and_selection_are_unchanged(self):
        callback = self.screen.split('void GeomScreen::GuiDeviceCallBack(', 1)[1]
        custom = callback.split('else if ( device == &m_CustomMaterialButton )', 1)[1].split(
            'else if ( device == &m_ScaleAcceptButton )', 1)[0]
        self.assertIn('custom.m_Name = "Custom";', custom)
        self.assertIn('geom_ptr->SetMaterial( custom );', custom)
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
        self.assertIn('display == m_DisplayLabels.end() ? label.c_str() : display->second.c_str()', update)
        self.assertIn('m_DisplayLabels.clear();', choice)
        self.assertIn('AddItemRaw( item );', choice)
        self.assertIn('m_DisplayLabels[m_Items.size() - 1] = label;', choice)


if __name__ == '__main__':
    unittest.main()
