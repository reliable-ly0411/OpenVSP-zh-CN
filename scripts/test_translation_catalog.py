#!/usr/bin/env python3
"""Regression tests for the translation guard, independent of the C++ driver."""
import unittest

from check_translation_catalog import extract_labels, read_catalogs, strip_comments


def table_source(exact, phrase):
    return ("ExactTranslations()\n{\n static auto table = {" + exact + "};\n}\n"
            "PhraseTranslations()\n{\n static auto rules = {" + phrase + "};\n}\n")


class CatalogGuardTests(unittest.TestCase):
    def test_duplicates_fail_even_with_same_translation(self):
        _, errors = read_catalogs(table_source('{"Name", "名称"}, {"Name", "名称"}', ''))
        self.assertTrue(any('duplicate key' in error for error in errors))

    def test_phrase_duplicates_fail(self):
        _, errors = read_catalogs(table_source('', '{"Top", "顶部"}, {"Top", "顶视图"}'))
        self.assertTrue(any('duplicate key' in error for error in errors))

    def test_exact_phrase_conflict_fails(self):
        _, errors = read_catalogs(table_source('{"Top", "顶视图"}', '{"Top", "顶部"}'))
        self.assertTrue(any('Conflicting' in error for error in errors))

    def test_consistent_tables_pass(self):
        tables, errors = read_catalogs(table_source('{"Name", "名称"}', '{"Name", "名称"}'))
        self.assertFalse(errors)
        self.assertEqual(tables['ExactTranslations']['Name'], '名称')

    def test_missing_tables_fail(self):
        _, errors = read_catalogs('')
        self.assertEqual(len(errors), 2)

    def test_comment_stripper_preserves_literal_slashes(self):
        source = 'AddItem("R//L"); // AddItem("ignore");\nAddItem("https://example.org/*test*/");'
        self.assertEqual(extract_labels(source), {'R//L', 'https://example.org/*test*/'})
        self.assertEqual(strip_comments(source).count('\n'), source.count('\n'))

    def test_block_comments_are_ignored(self):
        self.assertEqual(extract_labels('/* AddButton(x, "Ignore");\ncomment */\nAddTab("Wing");'), {'Wing'})

    def test_first_label_not_numeric_format(self):
        source = 'layout.AddSlider(slider, "Length", 1, "%6.4f"); layout.AddSlider(slider, eta, 1, "%6.4f");'
        self.assertEqual(extract_labels(source), {'Length'})

    def test_percent_labels_are_not_formats(self):
        self.assertEqual(extract_labels('AddItem("% Total"); AddItem("% of CD_Geom");'), {'% Total', '% of CD_Geom'})

    def test_multiline_strings_are_decoded(self):
        self.assertEqual(extract_labels('Alert("Line one\\nLine two");'), {'Line one\nLine two'})

    def test_browser_headers_and_chinese_have_separate_checks(self):
        self.assertEqual(extract_labels('browser.add("@b@.NAME"); AddItem("FEA 结构");'), set())

    def test_bypassed_english_labels_are_not_silently_ignored(self):
        self.assertEqual(extract_labels('AddDividerBox("New Mesh Control"); AddOutput(output, "Tip");'),
                         {'New Mesh Control', 'Tip'})


if __name__ == '__main__':
    unittest.main()
