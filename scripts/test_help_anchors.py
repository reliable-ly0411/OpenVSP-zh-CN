#!/usr/bin/env python3
"""Check every local help fragment independently of the Markdown generator.

Run: python3 scripts/test_help_anchors.py -v
Generator tests: node src/help/build_help_zh.js <node_modules> --test
Reproducibility: node src/help/build_help_zh.js <node_modules> --check
"""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
HELP = ROOT / "src" / "help"


class HelpPage(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = Counter()
        self.fragments = []
        self.headings = 0
        self.errors = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        line = self.getpos()[0]
        if "id" in attrs:
            if not attrs["id"]:
                self.errors.append(f"line {line}: empty id")
            self.ids[attrs["id"]] += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings += 1
            if not attrs.get("id"):
                self.errors.append(f"line {line}: <{tag}> is missing an id")
        if tag == "a" and attrs.get("href") and "#" in attrs["href"]:
            self.fragments.append((line, attrs["href"]))

    handle_startendtag = handle_starttag


def check_help_anchors(html_dir):
    """Return all problems and per-page counts; never fetch external URLs."""
    html_dir = Path(html_dir).resolve()
    pages = {
        path.resolve(): HelpPage(path.read_text(encoding="utf-8"))
        for path in sorted(html_dir.rglob("*.html"))
    }
    errors = []
    counts = {}
    if not pages:
        errors.append("No generated HTML help pages found.")
    for path, page in pages.items():
        name = path.relative_to(html_dir).as_posix()
        errors.extend(f"{name}: {error}" for error in page.errors)
        for identifier, count in page.ids.items():
            if count > 1:
                errors.append(f"{name}: duplicate id {identifier!r} ({count} occurrences)")
        local_fragments = 0
        for line, href in page.fragments:
            try:
                url = urlsplit(href)
                if url.scheme or url.netloc or not url.fragment:
                    # Empty fragments are valid links to the top of the page.
                    continue
                target = (path.parent / unquote(url.path, errors="strict")).resolve() if url.path else path
                fragment = unquote(url.fragment, errors="strict")
            except (UnicodeError, ValueError) as error:
                errors.append(f"{name}:{line}: invalid fragment URL {href!r}: {error}")
                continue
            if target.suffix.lower() != ".html":
                continue
            local_fragments += 1
            if target not in pages:
                errors.append(f"{name}:{line}: missing local help page for {href!r}")
            elif fragment not in pages[target].ids:
                errors.append(f"{name}:{line}: no id {fragment!r} for {href!r}")
        counts[name] = {"headings": page.headings, "fragments": local_fragments}
    return errors, counts


class BundledHelpTests(unittest.TestCase):
    def test_current_help_identity_preserves_original_attribution(self):
        for path in (HELP / "index.md", HELP / "html/index.html"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("非官方简体中文界面与帮助文档", text)
                self.assertIn("NASA/OpenVSP", text)
                self.assertIn("NOSA 1.3", text)
                self.assertNotIn("OpenAI", text)
                self.assertNotIn("Codex", text)

    def test_every_markdown_page_has_generated_html(self):
        sources = {path.stem for path in HELP.glob("*.md")}
        outputs = {path.stem for path in (HELP / "html").glob("*.html")}
        self.assertTrue(sources, "No Markdown help sources found")
        self.assertEqual(sources, outputs)

    def test_all_headings_and_fragment_targets(self):
        errors, counts = check_help_anchors(HELP / "html")
        self.assertEqual(errors, [], "\n".join(errors))
        # Keep the original regression cases visible; do not accidentally pass
        # by deleting the contents tables or the two inline geometry links.
        self.assertGreaterEqual(counts["GeometryAnalysis.html"]["fragments"], 22)
        self.assertGreaterEqual(counts["StackPresets.html"]["fragments"], 17)


class AnchorCheckerTests(unittest.TestCase):
    def check_pages(self, pages):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, text in pages.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            return check_help_anchors(root)

    def test_raw_and_percent_encoded_chinese_fragments(self):
        errors, counts = self.check_pages({"test.html": """
            <h2 id="中文">中文</h2><a href="#中文">raw</a>
            <a href="#%E4%B8%AD%E6%96%87">encoded</a>
        """})
        self.assertEqual(errors, [])
        self.assertEqual(counts["test.html"], {"headings": 1, "fragments": 2})

    def test_english_repeated_heading_targets(self):
        errors, _ = self.check_pages({"test.html": """
            <h2 id="openvsp-api">OpenVSP API</h2>
            <h3 id="openvsp-api-1">OpenVSP API</h3>
            <a href="#openvsp-api">first</a><a href="#openvsp-api-1">second</a>
        """})
        self.assertEqual(errors, [])

    def test_duplicate_ids_are_rejected(self):
        errors, _ = self.check_pages({"test.html": '<h2 id="中文">一</h2><h2 id="中文">二</h2>'})
        self.assertTrue(any("duplicate id '中文'" in error for error in errors), errors)

    def test_missing_heading_id_and_target_are_both_reported(self):
        errors, _ = self.check_pages({"test.html": '<h2>中文</h2><a href="#中文">link</a>'})
        self.assertEqual(len(errors), 2, errors)
        self.assertIn("missing an id", errors[0])
        self.assertIn("no id '中文'", errors[1])

    def test_every_broken_link_is_reported(self):
        errors, _ = self.check_pages({"test.html": '<a href="#one">1</a><a href="#two">2</a>'})
        self.assertEqual(len(errors), 2, errors)

    def test_empty_id_is_rejected(self):
        errors, _ = self.check_pages({"test.html": '<span id=""></span>'})
        self.assertTrue(any("empty id" in error for error in errors), errors)

    def test_cross_page_and_self_page_fragments(self):
        errors, counts = self.check_pages({
            "test.html": '<a href="sub/target.html#%E4%B8%AD%E6%96%87">next</a>',
            "sub/target.html": '<h2 id="中文">中文</h2><a href="target.html?view=1#中文">self</a>',
        })
        self.assertEqual(errors, [])
        self.assertEqual(counts["test.html"]["fragments"], 1)

    def test_missing_cross_page_target_is_rejected(self):
        errors, _ = self.check_pages({"test.html": '<a href="missing.html#中文">next</a>'})
        self.assertTrue(any("missing local help page" in error for error in errors), errors)

    def test_external_and_empty_fragments_are_ignored(self):
        errors, counts = self.check_pages({"test.html": """
            <a href="https://example.invalid/help.html#external">web</a>
            <a href="//example.invalid/help.html#external">web</a>
            <a href="#">top</a>
        """})
        self.assertEqual(errors, [])
        self.assertEqual(counts["test.html"]["fragments"], 0)

    def test_attribute_entities_are_decoded(self):
        errors, _ = self.check_pages({"test.html": '<span id="a&amp;b"></span><a href="#a%26b">link</a>'})
        self.assertEqual(errors, [])

    def test_invalid_percent_encoded_utf8_is_rejected(self):
        errors, _ = self.check_pages({"test.html": '<a href="#%ff">broken</a>'})
        self.assertTrue(any("invalid fragment URL" in error for error in errors), errors)

    def test_no_help_pages_is_rejected(self):
        errors, _ = self.check_pages({})
        self.assertEqual(errors, ["No generated HTML help pages found."])


if __name__ == "__main__":
    unittest.main()
