#!/usr/bin/env python3
"""Focused source regressions for reviewed OpenVSP 3.56.0 display labels.

The catalog CTest additionally executes all catalog_cases.json expectations
against the real C++ translator. These checks document engineering context.
"""
import json
from pathlib import Path
import unittest

from check_translation_catalog import read_catalogs

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / "src/gui_and_draw"
TESTS = ROOT / "scripts/localization_tests"


class Upstream356Labels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables, cls.errors = read_catalogs((GUI / "VSPChinese.cpp").read_text())
        cls.exact = cls.tables["ExactTranslations"]
        cls.reviewed = json.loads((TESTS / "catalog_cases.json").read_text())
        cls.preserved = json.loads((TESTS / "catalog_preserved.json").read_text())

    def assert_reviewed(self, cases):
        for label, expected in cases.items():
            with self.subTest(label=label):
                self.assertEqual(self.exact[label], expected)
                self.assertEqual(self.reviewed[label], expected)

    def test_catalog_has_no_duplicate_or_conflicting_entries(self):
        self.assertEqual(self.errors, [])

    def test_motion_modes_apply_to_all_hinges_not_only_pitch(self):
        source = (GUI / "PropScreen.cpp").read_text()
        for hinge in ("m_FlapAngleSlider", "m_LagAngleSlider", "m_HingeFeatherSlider"):
            self.assertIn("UpdateBladeSlider( " + hinge, source)
        self.assert_reviewed({"Collective": "统一", "Individual": "单独", "Ind.": "单独",
                              "Harmonic": "谐波", "Harmonics": "谐波阶数", "Lag": "摆振",
                              "Flapping": "挥舞"})
        self.assertEqual(self.exact["Flap"], "襟翼")

    def test_composed_rotor_labels_preserve_engineering_notation(self):
        cases = {"ψ Ref": "ψ 参考", "Azimuth (θ_F)": "方位角 (θ_F)",
                 "Azimuth (θ_L)": "方位角 (θ_L)", "Elevation (δ_3)": "仰角 (δ_3)",
                 "Cant (α_1)": "倾斜角 (α_1)"}
        for symbol in "βζθ":
            cases[f"Angle ({symbol})"] = f"角度 ({symbol})"
            cases[f"Mean ({symbol}0)"] = f"均值 ({symbol}0)"
        self.assert_reviewed(cases)

    def test_tire_and_mesh_terms(self):
        # GearGeom divides static loaded deflection by the above-flange height.
        source = (ROOT / "src/geom_core/GearGeom.cpp").read_text()
        self.assertIn("( 0.5 * Do - m_StaticRadiusIn() ) / Haboveflange", source)
        self.assert_reviewed({"Deflection Frac H": "挠度/H", "Surface Width": "曲面宽度",
                              "Num Width Segments": "宽度方向分段数", "Cull Tiny Edges": "剔除微小边",
                              "Merge Degen Tri Regions": "合并退化三角形区域"})

    def test_vector_formats_are_explicitly_preserved(self):
        for label in ("PDF", "SVG"):
            with self.subTest(label=label):
                self.assertTrue(self.preserved[label].strip())
                for table in self.tables.values():
                    self.assertEqual(table.get(label, label), label)
        self.assert_reviewed({"Vector Screenshot": "矢量截图", "Drawing": "绘图尺寸",
                              "Create or Select a Vector File": "创建或选择矢量文件",
                              "Could not write the vector file ": "无法写入矢量文件："})


if __name__ == "__main__":
    unittest.main()
