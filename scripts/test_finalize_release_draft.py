import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.update(GITHUB_REPOSITORY='example/repo', RELEASE_TAG='3.54.0-Codex-AI-zh-CN-r1',
                  SOURCE_COMMIT='b'*40, EXPECTED_DRAFT_SHA='a'*40, BUILD_RUN_ID='123')
spec = importlib.util.spec_from_file_location('finalize', Path(__file__).with_name('finalize_release_draft.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DraftGuards(unittest.TestCase):
    def test_published_release_is_never_modified(self):
        with patch.object(module, 'api', return_value=[{'draft': False, 'tag_name': module.TAG}]) as api:
            with self.assertRaisesRegex(ValueError, 'published'):
                module.guarded_draft()
        self.assertEqual(api.call_count, 1)

    def test_changed_tag_is_rejected(self):
        release = {'draft': True, 'prerelease': True, 'tag_name': module.TAG}
        with patch.object(module, 'api', side_effect=[[release], {'object': {'type': 'commit', 'sha': 'c'*40}}]):
            with self.assertRaisesRegex(ValueError, 'tag changed'):
                module.guarded_draft()

    def test_changed_assets_after_backup_block_all_mutations(self):
        release = {'id': 1, 'draft': True, 'prerelease': True, 'tag_name': module.TAG, 'assets': []}
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'plan.json').write_text('{}')
            with patch.object(module, 'WORK', Path(folder)), patch.object(module, 'guarded_draft', return_value=release), patch.object(module, 'api') as api:
                with self.assertRaisesRegex(ValueError, 'changed after backup'):
                    module.apply()
                api.assert_not_called()

    def test_draft_lookup_uses_list_endpoint_with_pagination(self):
        release = {'draft': True, 'tag_name': module.TAG}
        with patch.object(module, 'api', side_effect=[[{'tag_name': 'other'}]*100, [release]]) as api:
            self.assertEqual(module.find_release(), release)
            self.assertEqual(api.call_args_list[1].args[0], 'releases?per_page=100&page=2')


if __name__ == '__main__':
    unittest.main()
