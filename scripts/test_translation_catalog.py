#!/usr/bin/env python3
"""Regression tests for the translation guard, independent of the C++ driver."""
import unittest

from check_translation_catalog import (calls_display_helper, extract_labels, has_unconditional_translation_include,
                                       read_catalogs, strip_comments)


def table_source(exact, phrase):
    return ("ExactTranslations()\n{\n static auto table = {" + exact + "};\n}\n"
            "PhraseTranslations()\n{\n static auto rules = {" + phrase + "};\n}\n")


class CatalogGuardTests(unittest.TestCase):
    def test_all_display_only_helpers_are_guarded(self):
        for helper in ('BrowserHeader', 'LabelAndValue', 'Message'):
            with self.subTest(helper=helper):
                self.assertTrue(calls_display_helper('VSPTranslate' + helper + ' ( value );'))

    def test_commented_or_quoted_helper_calls_are_ignored(self):
        self.assertFalse(calls_display_helper('// VSPTranslateMessage(value);'))
        self.assertFalse(calls_display_helper('/* VSPTranslateLabelAndValue(title, value); */'))
        self.assertFalse(calls_display_helper('"VSPTranslateBrowserHeader(value)"'))

    def test_unconditional_helper_include(self):
        self.assertTrue(has_unconditional_translation_include('#include "VSPChinese.h"\n'))

    def test_windows_only_helper_include_is_not_sufficient(self):
        self.assertFalse(has_unconditional_translation_include(
            '#ifdef WIN32\n#include "VSPChinese.h"\n#endif\n'))

    def test_helper_include_after_conditional_is_valid(self):
        self.assertTrue(has_unconditional_translation_include(
            '#if defined(WIN32)\n#if X\n#endif\n#else\n#endif\n#include "VSPChinese.h"\n'))

    def test_commented_helper_include_is_not_sufficient(self):
        self.assertFalse(has_unconditional_translation_include('// #include "VSPChinese.h"\n'))

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
