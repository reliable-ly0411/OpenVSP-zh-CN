"""Issue #19 source contracts complement the real C++ translator tests.

These tests check UI ownership and enum wiring. They do not assert that a
native GUI has been displayed or that an independent specialist has signed off.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / "src/gui_and_draw"


class EngineeringTermContextTests(unittest.TestCase):
    def test_plan_is_the_wing_planform_tab(self):
        wing = (GUI / "WingScreen.cpp").read_text(encoding="utf-8")
        self.assertRegex(wing, r'plan_tab\s*=\s*AddTab\(\s*"Plan",\s*4\s*\)')
        self.assertIn('m_PlanLayout.AddDividerBox( "Total Planform" )', wing)
        plan_files = [path.name for path in GUI.glob("*.cpp")
                      if path.name != "VSPChinese.cpp"
                      and '"Plan"' in path.read_text(encoding="utf-8")]
        self.assertEqual(sorted(plan_files), ["WingScreen.cpp"])

    def test_end_caps_have_context_specific_display_keys_and_unchanged_enums(self):
        expected = {f"{name}Screen.cpp" for name in
                    ("Wing", "Prop", "Fuselage", "Stack", "Conformal")}
        found = set()
        pattern = r'\.AddItem\(\s*"([^"]+)",\s*vsp::(FLAT|ROUND)_END_CAP\s*\)'
        for path in GUI.glob("*.cpp"):
            pairs = re.findall(pattern, path.read_text(encoding="utf-8"))
            end_caps = [(label, kind) for label, kind in pairs if "End Cap" in label]
            if end_caps:
                found.add(path.name)
                self.assertEqual(end_caps.count(("Flat End Cap", "FLAT")), 2)
                self.assertEqual(end_caps.count(("Round End Cap", "ROUND")), 2)
            for label, kind in pairs:
                self.assertIn(label, (kind, kind.title() + " End Cap"))
        self.assertEqual(found, expected)

    def test_tire_flat_contact_does_not_acquire_an_end_cap_label(self):
        source = (GUI / "AuxiliaryGeomScreen.cpp").read_text(encoding="utf-8")
        labels = re.findall(r'AddItem\(\s*"([^"]+)",\s*vsp::TIRE_FLAT_CONTACT\s*\)', source)
        self.assertEqual(labels, ["Flat"] * 9)

    def test_airfoil_edge_cap_labels_remain_in_their_original_context(self):
        for name in ("WingScreen.cpp", "PropScreen.cpp", "BORScreen.cpp"):
            source = (GUI / name).read_text(encoding="utf-8")
            for end in ("LE", "TE"):
                for kind in ("FLAT", "ROUND"):
                    self.assertIn(f'm_{end}CapChoice.AddItem( "{kind}", vsp::{kind}_END_CAP )', source)

    def test_to_fem_is_a_converted_value_heading_not_a_conversion_button(self):
        counts = {}
        for path in GUI.glob("*.cpp"):
            if path.name == "VSPChinese.cpp":
                continue
            source = path.read_text(encoding="utf-8")
            count = source.count('"To FEM"')
            if count:
                counts[path.name] = count
                self.assertEqual(len(re.findall(r'AddDividerBox\(\s*"To FEM"\s*\)', source)), count)
        self.assertEqual(counts, {"StructScreen.cpp": 9, "FeaPartEditScreen.cpp": 1})
        fea = (ROOT / "src/geom_core/FeaStructure.cpp").read_text(encoding="utf-8")
        self.assertIn('m_FixPointMass_FEM = ConvertMass( m_FixPointMass(), m_MassUnit(), mass_unit );', fea)
        self.assertIn('m_CrossSecArea_FEM = ConvertLength2( m_CrossSecArea.Get(), m_LengthUnit(), length_unit );', fea)

    def test_activity_factor_is_the_single_blade_geometry_integral(self):
        source = (GUI / "PropScreen.cpp").read_text(encoding="utf-8")
        self.assertRegex(source, r'AddOutput\(\s*m_AFOutput,\s*"Activity Factor"')
        prop = (ROOT / "src/geom_core/PropGeom.cpp").read_text(encoding="utf-8")
        self.assertIn('m_AF.Init( "AF", "Design",', prop)
        self.assertIn('m_AF.Set( ( 100000.0 / 16.0 ) * 0.5 * m_ChordCurve.IntegrateCrv_rcub( m_AFLimit() ) );', prop)

    def test_transverse_isotropy_keeps_the_orthotropic_material_enum(self):
        source = (GUI / "StructScreen.cpp").read_text(encoding="utf-8")
        self.assertIn('AddItem( "Orthotropic w/ Transverse Isotropy", vsp::FEA_ENG_ORTHO_TRANS_ISO )', source)
        fea = (ROOT / "src/geom_core/FeaStructure.cpp").read_text(encoding="utf-8")
        for constraint in ("m_E3 = m_E2();", "m_G13 = m_G12();", "m_nu13 = m_nu12();",
                           "m_G23 = m_E2() / ( 2.0 * (1.0 + m_nu23() ) );"):
            self.assertIn(constraint, fea)

    def test_covert_remains_a_formula_name_in_both_dropdowns(self):
        source = (GUI / "ParasiteDragScreen.cpp").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r'm_ffType\[index\]\.AddItem\(\s*"Covert"\s*\)', source)), 2)
        enums = (ROOT / "src/geom_api/APIDefines.h").read_text(encoding="utf-8")
        self.assertIn("FF_B_COVERT", enums)
        self.assertIn("FF_W_COVERT", enums)


if __name__ == "__main__":
    unittest.main()
