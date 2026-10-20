"""Complete licensed upstream text and downstream release presentation contracts."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from native_plan import PLATFORMS, asset_name
from native_release import release_body
from upstream_release_notes import NOTES, upstream_release_notes


VERSIONS = ('3.51.2', '3.51.3', '3.53.0', '3.54.0', '3.55.0')


class UpstreamReleaseNotesTests(unittest.TestCase):
    def test_every_family_keeps_the_exact_complete_section(self):
        for version in VERSIONS:
            with self.subTest(version=version):
                entry, original = upstream_release_notes(version)
                body = release_body(version + '-zh-CN.rc.2', 'a' * 40, 'example/repo', True)
                self.assertIn(original, body)
                self.assertEqual(hashlib.sha256(original.encode()).hexdigest(), entry['section_sha256'])
                self.assertIn(entry['source_url'], body)
                self.assertIn(entry['announcement_url'], body)
                self.assertIn(entry['license_url'], body)
                self.assertIn('没有 GitHub Release', body)
                self.assertIn('上游作者原文', body)
                self.assertIn('社区模型', body)
                self.assertIn(version + '-zh-CN.rc.2', body)
                for platform in PLATFORMS:
                    self.assertIn(asset_name(version, platform['platform']), body)

    def test_mutation_truncation_and_wrong_version_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / 'notes'
            shutil.copytree(NOTES, copied)
            path = copied / '3.55.0.md'
            original = path.read_bytes()
            for raw in (original[:-1], original.replace(b'Features:', b'Features?'), b'# summary only\n'):
                path.write_bytes(raw)
                with self.assertRaises(ValueError):
                    upstream_release_notes('3.55.0', copied)
            for version in ('3.56.0', '../3.55.0', '3.55.0/other', '3.55.0\n'):
                with self.assertRaises(ValueError):
                    upstream_release_notes(version, copied)

    def test_source_commit_and_license_identity_are_not_arbitrary_urls(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / 'notes'
            shutil.copytree(NOTES, copied)
            path = copied / 'sources.json'
            original = path.read_text()
            for field, value in (('upstream_sha', 'main'), ('source_url', 'https://example.invalid/CHANGELOG.md'),
                                 ('license_url', 'https://example.invalid/LICENSE'),
                                 ('announcement_url', 'https://example.invalid/announcement')):
                catalog = json.loads(original)
                catalog['versions']['3.55.0'][field] = value
                path.write_text(json.dumps(catalog))
                with self.assertRaises(ValueError):
                    upstream_release_notes('3.55.0', copied)

    def test_rc1_text_does_not_claim_later_product_fixes(self):
        for version in VERSIONS:
            old = release_body(version + '-zh-CN.rc.1', 'a' * 40, 'example/repo', True)
            new = release_body(version + '-zh-CN.rc.2', 'a' * 40, 'example/repo', True)
            self.assertNotIn('rc.2 新增', old)
            self.assertIn('rc.2 新增', new)
            local = new.split('## 上游版本说明')[0]
            self.assertNotIn('Codex-AI', local)
            if version in ('3.54.0', '3.55.0'):
                self.assertIn('分割与缝合', local)
            else:
                self.assertNotIn('分割与缝合', local)

    def test_actual_platform_differences_and_gui_limits_are_explicit(self):
        for version in VERSIONS:
            body = release_body(version + '-zh-CN.rc.2', 'a' * 40, 'example/repo', True)
            self.assertIn('`.deb`', body)
            self.assertIn('便携 ZIP', body)
            self.assertIn('GUI 未作同范围人工验收', body)
            self.assertIn('ad-hoc', body)
            self.assertIn('尚未公证', body)
            if version in ('3.54.0', '3.55.0'):
                self.assertIn('官方此版本 ARM64 下载名使用 macOS 15', body)
            if version == '3.51.2':
                self.assertIn('尚未接续该官方标签的 Git 祖先', body)
        pending = release_body('3.55.0-zh-CN.rc.2', 'a' * 40, 'example/repo')
        self.assertIn('待目视', pending)
        self.assertNotIn('已人工抽查', pending)

    def test_release_links_reject_untrusted_repository_shape(self):
        for repository in ('example/repo?q=1', 'example/repo/other', 'https://example.com', 'a\nb/c'):
            with self.assertRaises(ValueError):
                release_body('3.55.0-zh-CN.rc.2', 'a' * 40, repository)


if __name__ == '__main__':
    unittest.main()
