import hashlib
from pathlib import Path
import tempfile
import unittest
from release_asset_names import asset_name, asset_candidates, normalize, verify_download

TAG = '3.55.0-Codex-AI-zh-CN-auto.' + 'a' * 12
PLATFORMS = ['Ubuntu-24.04-x86_64', 'Windows-x64']


class AssetNames(unittest.TestCase):
    def fixture(self, directory, legacy=False):
        directory.mkdir()
        rows = []
        for platform in PLATFORMS:
            name = asset_candidates(TAG, platform)[int(legacy)]
            data = platform.encode()
            (directory / name).write_bytes(data)
            rows.append(f'{hashlib.sha256(data).hexdigest()}  ./{name}\n')
        (directory / 'SHA256SUMS.txt').write_text(''.join(rows))

    def test_names_follow_platform_style_without_changing_tags(self):
        self.assertEqual(asset_name(TAG, PLATFORMS[0]), 'OpenVSP-3.55.0-Ubuntu-24.04_amd64-zh-CN.zip')
        self.assertEqual(asset_name(TAG, PLATFORMS[1]), 'OpenVSP-3.55.0-win64-zh-CN.zip')
        with self.assertRaises(ValueError):
            asset_name('../bad-tag', PLATFORMS[0])
        with self.assertRaises(ValueError):
            asset_name(TAG, '../windows')

    def test_legacy_and_new_drafts_verify_by_bytes(self):
        for legacy in (False, True):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self.fixture(root/'expected')
                self.fixture(root/'actual', legacy)
                verify_download(root/'expected', root/'actual', TAG)
                name = asset_candidates(TAG, PLATFORMS[0])[int(legacy)]
                (root/'actual'/name).write_bytes(b'changed')
                with self.assertRaises(ValueError):
                    verify_download(root/'expected', root/'actual', TAG)

    def test_rename_is_byte_preserving_and_rejects_duplicates_before_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root/'packages', True)
            folder = root/'packages'
            new, old = asset_candidates(TAG, PLATFORMS[0])
            (folder/new).write_bytes(b'conflict')
            with self.assertRaises(ValueError):
                normalize(folder, TAG)
            self.assertTrue((folder/old).exists())
            (folder/new).unlink()
            normalize(folder, TAG)
            for platform in PLATFORMS:
                self.assertEqual((folder/asset_name(TAG,platform)).read_bytes(), platform.encode())

    def test_checksum_missing_extra_duplicate_and_wrong_hash_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.fixture(root/'expected');self.fixture(root/'actual')
            manifest=root/'actual'/'SHA256SUMS.txt'
            original=manifest.read_text()
            for content in ('',original+original,original+'0'*64+'  ../escape\n','0'*64+original[64:]):
                manifest.write_text(content)
                with self.assertRaises(ValueError):
                    verify_download(root/'expected',root/'actual',TAG)

if __name__ == '__main__':
    unittest.main()
