import unittest
from release_notes import release_title, release_body, update_notes


class ReleaseNotesTests(unittest.TestCase):
    def test_titles_preserve_revision_and_prerelease(self):
        self.assertEqual(release_title('3.54.0-Codex-AI-zh-CN'), 'OpenVSP 3.54.0 Codex AI 简体中文版')
        self.assertEqual(release_title('3.54.0-Codex-AI-zh-CN-r1', True), 'OpenVSP 3.54.0 Codex AI 简体中文版（r1 · 预发布）')
        self.assertEqual(release_title('3.54.0-Codex-AI-zh-CN-auto.'+'a'*12), 'OpenVSP 3.54.0 Codex AI 简体中文版（自动预发布 · '+'a'*12+'）')
        with self.assertRaises(ValueError):
            release_title('bad-tag')

    def test_same_structure_and_exact_downloads(self):
        for tag in ['3.54.0-Codex-AI-zh-CN-r1','3.54.0-Codex-AI-zh-CN-auto.'+'a'*12]:
            body = release_body(tag, '- 当前修复', 'owner/repo', 'b'*40, '123', True)
            self.assertEqual([line for line in body.splitlines() if line.startswith('## ')],
                             ['## 版本信息','## 本次更新','## 下载与校验','## 验证情况','## 兼容性与限制','## 许可与归属'])
            for platform in ['Ubuntu-24.04-x86_64','Windows-x64']:
                self.assertIn(f'/releases/download/{tag}/OpenVSP-{tag}-{platform}.zip', body)
            self.assertIn('/actions/runs/123',body)
            self.assertIn('当前修复',body)
            self.assertNotIn('GUI 全面验收通过',body)

    def test_historical_notes_not_mixed_into_new_release(self):
        self.assertEqual(update_notes('## v-new\n- new\n\n## v-old\n- old\n','v-new'), '- new')
        with self.assertRaises(ValueError):
            update_notes('## v-new\n\n## v-old\n- old\n','v-new')
