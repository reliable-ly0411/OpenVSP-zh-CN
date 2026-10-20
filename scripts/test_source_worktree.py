"""Test actual Git status, including non-ignored untracked files."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_source_worktree import source_status, require_clean_source


class SourceWorktreeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Worktree test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.root / 'tracked').write_text('unchanged')
        (self.root / '.gitignore').write_text('build/\nbuildlibs/\n')
        self.git('add', '.'); self.git('commit', '-m', 'baseline')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)

    def test_ignored_build_outputs_are_not_source_changes(self):
        (self.root / 'build').mkdir(); (self.root / 'build/out').write_text('generated')
        self.assertEqual(source_status(self.root), '')
        self.assertTrue(require_clean_source(self.root))

    def test_untracked_source_is_rejected(self):
        (self.root / 'extra.py').write_text('unexpected')
        with self.assertRaisesRegex(ValueError, 'extra.py'):
            require_clean_source(self.root)

    def test_tracked_and_staged_changes_are_rejected(self):
        (self.root / 'tracked').write_text('changed')
        with self.assertRaises(ValueError): require_clean_source(self.root)
        self.git('add', 'tracked')
        with self.assertRaises(ValueError): require_clean_source(self.root)


if __name__ == '__main__': unittest.main()
