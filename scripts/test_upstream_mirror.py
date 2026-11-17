"""Offline Git-graph regressions for exact mirrors and README compare direction."""

import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import sync_upstream_mirror as mirror

ROOT = Path(__file__).resolve().parents[1]


class MirrorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.upstream = root / 'upstream'
        self.destination = root / 'destination.git'
        self.work = root / 'work'
        self.git(root, 'init', '--bare', str(self.destination))
        self.git(root, 'init', '-b', 'main', str(self.upstream))
        self.git(self.upstream, 'config', 'user.name', 'Mirror test')
        self.git(self.upstream, 'config', 'user.email', 'test@example.invalid')
        self.base = self.commit(self.upstream, 'official baseline')
        self.git(self.upstream, 'push', str(self.destination), 'main')
        self.git(root, 'clone', '-b', 'main', str(self.destination), str(self.work))
        self.git(self.work, 'config', 'user.name', 'Mirror test')
        self.git(self.work, 'config', 'user.email', 'test@example.invalid')
        self.original_cwd = Path.cwd()
        os.chdir(self.work)
        self.addCleanup(os.chdir, self.original_cwd)

    def git(self, repo, *args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True,
                                       stderr=subprocess.PIPE).strip()

    def commit(self, repo, message):
        self.git(repo, 'commit', '--allow-empty', '-m', message)
        return self.git(repo, 'rev-parse', 'HEAD')

    def sync(self):
        return mirror.sync(str(self.upstream), str(self.destination))

    def test_create_unchanged_and_fast_forward_leave_main_head_and_tags_alone(self):
        self.git(self.destination, 'tag', 'historical', self.base)
        self.git(self.destination, 'branch', 'develop/3.51.2-zh-CN', self.base)
        refs_before = self.git(self.destination, 'show-ref')
        result = self.sync()
        self.assertEqual((result['before'], result['after'], result['action']), (None, self.base, 'created'))
        with patch.object(mirror, 'git', wraps=mirror.git) as calls:
            self.assertEqual(self.sync()['action'], 'unchanged')
            self.assertFalse(any(c.args[0] == 'push' for c in calls.call_args_list))
        update = self.commit(self.upstream, 'upstream advances')
        result = self.sync()
        self.assertEqual((result['before'], result['after'], result['action']), (self.base, update, 'fast-forward'))
        self.assertEqual((result['ahead_by'], result['behind_by']), (0, 1))
        self.assertEqual(self.git(self.work, 'rev-parse', 'HEAD'), self.base)
        refs_after = '\n'.join(row for row in self.git(self.destination, 'show-ref').splitlines()
                               if not row.endswith(' ' + mirror.MIRROR))
        self.assertEqual(refs_after, refs_before)
        self.assertEqual(self.git(self.destination, 'rev-parse', mirror.MIRROR), update)

    def test_comparison_zero_ahead_behind_and_diverged(self):
        self.assertEqual(mirror.counts(self.base, self.base), dict(ahead_by=0, behind_by=0))
        localized = self.commit(self.work, 'localization')
        self.assertEqual(mirror.counts(self.base, localized), dict(ahead_by=1, behind_by=0))
        self.assertEqual(mirror.counts(localized, self.base), dict(ahead_by=0, behind_by=1))
        self.git(self.work, 'push', str(self.destination), 'main')
        self.commit(self.upstream, 'official one')
        self.commit(self.upstream, 'official two')
        result = self.sync()
        self.assertEqual((result['ahead_by'], result['behind_by']), (1, 2))
        self.assertEqual(result['localized_main'], localized)

    def test_rewind_or_divergence_refuses_to_rewrite_mirror(self):
        update = self.commit(self.upstream, 'official advance')
        self.sync()
        self.git(self.upstream, 'reset', '--hard', self.base)
        for diverged in (False, True):
            if diverged:
                self.commit(self.upstream, 'rewritten upstream')
            with self.subTest(diverged=diverged), self.assertRaises(subprocess.CalledProcessError):
                self.sync()
            self.assertEqual(self.git(self.destination, 'rev-parse', mirror.MIRROR), update)

    def test_normal_push_rejects_concurrent_divergence(self):
        self.sync()
        self.commit(self.upstream, 'official advance')
        competing = self.commit(self.work, 'concurrent unrelated mirror update')
        original = mirror.git
        def race(*args):
            if args[0] == 'push':
                self.git(self.work, 'push', str(self.destination), f'{competing}:{mirror.MIRROR}')
            return original(*args)
        with patch.object(mirror, 'git', side_effect=race), self.assertRaises(subprocess.CalledProcessError):
            self.sync()
        self.assertEqual(self.git(self.destination, 'rev-parse', mirror.MIRROR), competing)

    def test_failed_push_is_not_reported_as_success(self):
        # Inject a remote permission/network rejection at the push boundary.
        original = mirror.git
        def reject(*args):
            if args[0] == 'push':
                raise subprocess.CalledProcessError(1, ['git', *args])
            return original(*args)
        with patch.object(mirror, 'git', side_effect=reject), self.assertRaises(subprocess.CalledProcessError):
            self.sync()
        self.assertIsNone(mirror.remote_sha(str(self.destination), mirror.MIRROR))

    def test_shallow_checkout_is_rejected_before_network(self):
        with patch.object(mirror, 'git', return_value='true') as calls:
            with self.assertRaisesRegex(RuntimeError, 'full history'):
                self.sync()
        calls.assert_called_once_with('rev-parse', '--is-shallow-repository')


class BadgeContractTests(unittest.TestCase):
    def test_both_readmes_use_live_compare_with_correct_direction_and_cache(self):
        repo = 'https://github.com/reliable-ly0411/OpenVSP-zh-CN'
        api = 'https://api.github.com/repos/reliable-ly0411/OpenVSP-zh-CN/compare/upstream-main...main'
        for path in ('README.md', 'README_zh-CN.md'):
            text = (ROOT / path).read_text()
            badges = re.findall(r'\[!\[[^]]+\]\((https://img.shields.io/[^)]+)\)\]\(([^)]+)\)', text)
            self.assertEqual(len(badges), 2, path)
            for (url, link), field, color, compare in zip(badges,
                    ('ahead_by', 'behind_by'), ('blue', 'orange'),
                    ('upstream-main...main', 'main...upstream-main')):
                query = parse_qs(urlparse(url).query)
                self.assertEqual(query['url'], [api])
                self.assertEqual(query['query'], ['$.' + field])
                self.assertEqual(query['color'], [color])
                self.assertEqual(query['cacheSeconds'], ['300'])
                self.assertEqual(link, repo + '/compare/' + compare)
            self.assertIn('https://github.com/OpenVSP/OpenVSP', text)
            self.assertIn('https://openvsp.org/', text)

    def test_mirror_runs_only_on_main_daily_or_manual_with_scoped_builtin_token(self):
        text = (ROOT / '.github/workflows/upstream-watch.yml').read_text()
        job = text.split('\n  mirror:\n')[1].split('\n  policy-checks:')[0]
        self.assertIn("github.ref == 'refs/heads/main'", job)
        self.assertIn("github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'", job)
        self.assertNotIn('needs:', job)
        self.assertIn('ref: main', job)
        self.assertIn('persist-credentials: false', job)
        self.assertIn('PUSH_TOKEN: ${{ github.token }}', job)
        self.assertIn('http.https://github.com/reliable-ly0411/OpenVSP-zh-CN.git.extraheader', job)
        self.assertIn('python3 -I scripts/sync_upstream_mirror.py', job)
        self.assertNotIn('--force', (ROOT / 'scripts/sync_upstream_mirror.py').read_text())
        from sync_upstream import TRUSTED_POLICY_PATHS
        self.assertIn('scripts/sync_upstream_mirror.py', TRUSTED_POLICY_PATHS)
        self.assertIn('scripts/test_upstream_mirror.py', TRUSTED_POLICY_PATHS)


if __name__ == '__main__':
    unittest.main()
