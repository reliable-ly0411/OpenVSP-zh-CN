from pathlib import Path
import unittest
from upstream_ui_report import added_literals


class AddedLiteralTests(unittest.TestCase):
    def test_lines_catalog_hits_and_non_ui_strings_are_only_evidence(self):
        diff = '''diff --git a/src/gui_and_draw/Test.cpp b/src/gui_and_draw/Test.cpp
--- a/src/gui_and_draw/Test.cpp
+++ b/src/gui_and_draw/Test.cpp
@@ -2,0 +3,2 @@
+layout.AddButton("New control");
+layout.AddButton("Known control");
@@ -20 +22 @@
-old_line("removed")
+value = "ParmID";
'''
        rows = added_literals(diff, '{ "Known control", "已有控件" },')
        self.assertEqual([r['line'] for r in rows], [3, 4, 22])
        self.assertEqual([r['exact_catalog_key'] for r in rows], [False, True, False])
        self.assertEqual(rows[2]['literal'], 'ParmID')
        self.assertTrue(all(r['path'] == 'src/gui_and_draw/Test.cpp' for r in rows))

    def test_escaped_literals_are_preserved_as_data(self):
        rows = added_literals('+++ b/src/gui_and_draw/Test.cpp\n@@ -1 +1 @@\n+label("hello \\\"world\\\"");', '')
        self.assertEqual(rows[0]['literal'], 'hello \\"world\\"')

    def test_no_added_strings_produces_no_claims(self):
        self.assertEqual(added_literals('+++ b/src/gui_and_draw/Test.cpp\n@@ -1 +1 @@\n-old("removed")\n+function();', ''), [])


if __name__ == '__main__': unittest.main()
