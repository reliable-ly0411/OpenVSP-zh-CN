#!/usr/bin/env python3
"""Exercise upstream synchronization with real temporary Git repositories."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name('sync_upstream.py').resolve()


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-b', 'official')
        self.git('config', 'user.name', 'Sync test')
        self.git('config', 'user.email', 'sync@example.invalid')
        self.write('src/cmake/VSP_Version.cmake', 'SET( VSPVER_MAJOR 3 )\nSET( VSPVER_MINOR 53 )\nSET( VSPVER_PATCH 0 )\n')
        self.write('src/gui_and_draw/MainVSPScreen.cpp', 'upstream code\n')
        self.write('core.txt', 'original\n')
        self.write('.github/workflows/build.yml', 'official workflow\n')
        self.commit('official baseline')
        self.baseline = self.git('rev-parse', 'HEAD').strip()
        self.git('checkout', '-b', 'localized')
        self.write('.github/upstream.json', json.dumps({'repository': 'OpenVSP/OpenVSP', 'branch': 'main', 'base_commit': self.baseline, 'version': '3.53.0'}))
        self.write('README.md', '本仓库基于 OpenVSP 3.53.0，中文说明\n')
        self.history = '## 3.53.0-Codex-AI-zh-CN\n历史版本 3.53.0 不应改变\n'
        self.write('README_zh-CN.md', '当前软件版本：OpenVSP 3.53.0\n当前汉化版本：`3.53.0-Codex-AI-zh-CN`\n## 未发布\n\n' + self.history)
        self.write('AGENTS.md', f'当前官方基线：OpenVSP 3.53.0，提交\n  `{self.baseline}`；其他规则\n')
        self.write('src/gui_and_draw/MainVSPScreen.cpp', 'upstream code\n"汉化版本：3.53.0-Codex-AI-zh-CN\\n"\n')
        self.write('.github/workflows/build.yml', 'localized workflow\n')
        self.commit('localization')
        self.localized = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args, check=True):
        result = subprocess.run(['git', *args], cwd=self.root, text=True, capture_output=True, check=check)
        return result.stdout

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def commit(self, message):
        self.git('add', '--all')
        self.git('commit', '-m', message)

    def upstream_update(self, conflict=False, workflow_delete=False):
        self.git('checkout', 'official')
        self.write('src/cmake/VSP_Version.cmake', 'SET( VSPVER_MAJOR 3 )\nSET( VSPVER_MINOR 54 )\nSET( VSPVER_PATCH 0 )\n')
        self.write('core.txt', 'official update\n')
        if workflow_delete:
            self.git('rm', '.github/workflows/build.yml')
        else:
            self.write('.github/workflows/build.yml', 'new official workflow\n')
        self.write('.github/workflows/new-official.yml', 'new official CI\n')
        self.commit('upstream update')
        upstream = self.git('rev-parse', 'HEAD').strip()
        self.git('checkout', 'localized')
        if conflict:
            self.write('core.txt', 'localized modification\n')
            self.commit('local code modification')
        return upstream

    def run_sync(self, ref='official'):
        return subprocess.run([sys.executable, str(SCRIPT), ref], cwd=self.root, text=True, capture_output=True)

    def test_merge_keeps_both_parents_and_local_workflows(self):
        upstream = self.upstream_update()
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'core.txt').read_text(), 'official update\n')
        self.assertEqual((self.root / '.github/workflows/build.yml').read_text(), 'localized workflow\n')
        self.assertFalse((self.root / '.github/workflows/new-official.yml').exists())
        metadata = json.loads((self.root / '.github/upstream.json').read_text())
        self.assertEqual((metadata['version'], metadata['base_commit']), ('3.54.0', upstream))
        notes = (self.root / 'README_zh-CN.md').read_text()
        self.assertIn('当前软件版本：OpenVSP 3.54.0', notes)
        self.assertTrue(notes.endswith(self.history))
        self.assertIn('## 3.54.0-Codex-AI-zh-CN-auto.' + upstream[:12], notes)
        self.git('commit', '-m', 'validated merge')
        self.assertEqual(self.git('rev-list', '--parents', '-n', '1', 'HEAD').split()[1:], [self.localized, upstream])
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['changed'], 'false')

    def test_workflow_delete_conflict_keeps_local_policy(self):
        self.upstream_update(workflow_delete=True)
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / '.github/workflows/build.yml').read_text(), 'localized workflow\n')
        self.assertEqual(self.git('diff', '--name-only', '--diff-filter=U'), '')

    def test_code_conflict_does_not_commit_or_advance_baseline(self):
        self.upstream_update(conflict=True)
        before = self.git('rev-parse', 'HEAD')
        result = self.run_sync()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('core.txt', result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        self.assertEqual(json.loads((self.root / '.github/upstream.json').read_text())['base_commit'], self.baseline)

    def test_no_update_has_no_file_changes(self):
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['changed'], 'false')
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_normal_push_rejects_concurrent_main_update(self):
        self.upstream_update()
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git('commit', '-m', 'candidate')
        candidate = self.git('rev-parse', 'HEAD').strip()
        # 使用裸仓库复现构建期间 main 被他人推进，不允许发布候选覆盖该提交。
        remote = self.root / 'remote.git'
        self.git('init', '--bare', str(remote))
        self.git('push', str(remote), f'{self.localized}:refs/heads/main')
        self.git('checkout', '-b', 'concurrent', self.localized)
        self.write('concurrent.txt', 'keep this update\n')
        self.commit('concurrent main update')
        concurrent = self.git('rev-parse', 'HEAD').strip()
        self.git('push', str(remote), 'HEAD:refs/heads/main')
        result = subprocess.run(['git', 'push', str(remote), f'{candidate}:refs/heads/main'], cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git('--git-dir', str(remote), 'rev-parse', 'main').strip(), concurrent)


if __name__ == '__main__':
    unittest.main()
