#!/usr/bin/env python3
"""Test release notes, platform pairing and byte-preserving published assets."""

import hashlib
from pathlib import Path
import tempfile
import unittest

from check_localization_release import TAG_RE
from prepare_auto_release import automatic_tag, prepare_assets, update_notes


class AutoReleaseTests(unittest.TestCase):
    def test_tag_binds_version_and_upstream_commit(self):
        tag = automatic_tag({'version': '3.54.0', 'base_commit': 'a' * 40})
        self.assertEqual(tag, '3.54.0-Codex-AI-zh-CN-auto.' + 'a' * 12)
        self.assertEqual(TAG_RE.fullmatch(tag).group('upstream'), 'a' * 12)
        self.assertIsNone(TAG_RE.fullmatch(tag + '-unexpected'))
        self.assertIsNotNone(TAG_RE.fullmatch('3.54.0-Codex-AI-zh-CN-r2'))

    def test_notes_exclude_unreleased_and_older_sections(self):
        tag = '3.54.0-Codex-AI-zh-CN-auto.' + 'a' * 12
        text = f'## 未发布\n后续维护\n\n## {tag}\n\n本次更新\n\n## 3.53.0-Codex-AI-zh-CN\n旧记录\n'
        self.assertEqual(update_notes(text, tag), '本次更新')

    def test_missing_notes_stop_publication(self):
        with self.assertRaises(ValueError):
            update_notes('## 未发布\n只有未发布记录\n', '3.54.0-Codex-AI-zh-CN-auto.' + 'a' * 12)

    def test_assets_and_checksums_preserve_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packages = root / 'packages'
            packages.mkdir()
            source_sha = 'b' * 40
            tag = '3.54.0-Codex-AI-zh-CN-auto.' + 'a' * 12
            payloads = {'Ubuntu-24.04-x86_64': b'linux zip payload', 'Windows-x64': b'windows zip payload'}
            for platform, data in payloads.items():
                (packages / f'OpenVSP-{source_sha}-{platform}.zip').write_bytes(data)
            output = root / 'release'
            prepare_assets(packages, output, source_sha, tag)
            manifest = (output / 'SHA256SUMS.txt').read_text()
            for platform, data in payloads.items():
                filename = f'OpenVSP-{tag}-{platform}.zip'
                self.assertEqual((output / filename).read_bytes(), data)
                self.assertIn(f'{hashlib.sha256(data).hexdigest()}  {filename}\n', manifest)

    def test_missing_platform_or_mixed_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ('OpenVSP-' + 'b' * 40 + '-Ubuntu-24.04-x86_64.zip')).write_bytes(b'linux')
            for mixed in (False, True):
                with self.subTest(mixed=mixed):
                    if mixed:
                        (root / ('OpenVSP-' + 'c' * 40 + '-Windows-x64.zip')).write_bytes(b'windows')
                    with self.assertRaises(ValueError):
                        prepare_assets(root, root / 'release', 'b' * 40, 'auto-tag')
                    self.assertFalse((root / 'release').exists())


if __name__ == '__main__':
    unittest.main()
