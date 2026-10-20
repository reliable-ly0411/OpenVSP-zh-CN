"""Real Git graph tests; remote writes below are isolated test fixtures only."""
from contextlib import chdir
import shutil
import unittest
from unittest.mock import patch

import upstream_candidate
import test_sync_upstream as sync_fixtures


class CandidateIdentityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = sync_fixtures.SyncTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.git = self.fixture.git
        self.upstream = self.fixture.upstream_update()
        result = self.fixture.run_sync(source_ref="main")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.remote = self.fixture.root.parent / (self.fixture.root.name + "-remote.git")
        self.git("init", "--bare", str(self.remote))
        self.addCleanup(shutil.rmtree, self.remote)
        self.git("remote", "add", "origin", str(self.remote))
        self.branch = upstream_candidate.candidate_branch(self.fixture.localized, self.upstream, "main")
        self.tree = self.git("write-tree").strip()

    def inspect(self, source_ref="main"):
        with chdir(self.fixture.root):
            return upstream_candidate.inspect_candidate(self.upstream, source_ref)

    def seed_remote(self, tree=None, parents=None):
        parents = parents if parents is not None else [self.fixture.localized, self.upstream]
        arguments = ["commit-tree", tree or self.tree, "-m", "Candidate fixture"]
        for parent in parents:
            arguments.extend(["-p", parent])
        sha = self.git(*arguments).strip()
        self.git("push", "origin", f"{sha}:refs/heads/{self.branch}")
        return sha

    def test_new_source_pair_is_created_without_remote_mutation(self):
        before = self.git("ls-remote", "--heads", "origin")
        result = self.inspect()
        self.assertEqual(result, {"branch": self.branch, "changed": "true", "sha": ""})
        self.assertEqual(self.git("ls-remote", "--heads", "origin"), before)

    def test_existing_matching_tree_and_both_parents_are_reused_read_only(self):
        sha = self.seed_remote()
        before = self.git("ls-remote", "--heads", "origin")
        for _ in range(2):
            self.assertEqual(self.inspect(), {"branch": self.branch, "changed": "false", "sha": sha})
        self.assertEqual(self.git("ls-remote", "--heads", "origin"), before)
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), self.fixture.localized)

    def test_divergent_tree_is_rejected_without_overwriting(self):
        old_tree = self.git("rev-parse", f"{self.fixture.localized}^{{tree}}").strip()
        sha = self.seed_remote(tree=old_tree)
        with self.assertRaisesRegex(ValueError, "tree differs"):
            self.inspect()
        self.assertIn(sha, self.git("ls-remote", "--heads", "origin"))

    def test_wrong_or_reversed_parents_are_rejected(self):
        self.seed_remote(parents=[self.upstream, self.fixture.localized])
        with self.assertRaisesRegex(ValueError, "parents"):
            self.inspect()

    def test_snapshot_ref_and_version_tag_cannot_share_candidate_identity(self):
        self.seed_remote()
        self.assertEqual(self.inspect("OpenVSP_3.54.0")["changed"], "true")
        changed_base = upstream_candidate.candidate_branch("a" * 40, self.upstream, "main")
        changed_upstream = upstream_candidate.candidate_branch(self.fixture.localized, "b" * 40, "main")
        self.assertEqual(len({self.branch, changed_base, changed_upstream}), 3)

    def test_remote_lookup_failure_is_not_treated_as_absence(self):
        self.git("remote", "set-url", "origin", str(self.remote / "does-not-exist"))
        with self.assertRaisesRegex(RuntimeError, "lookup failed"):
            self.inspect()

    def test_candidate_moved_during_read_is_rejected(self):
        self.seed_remote()
        original = upstream_candidate.git
        def raced(*args, **kwargs):
            result = original(*args, **kwargs)
            if args == ("rev-parse", "FETCH_HEAD^{commit}"):
                result.stdout = "c" * 40 + "\n"
            return result
        with patch.object(upstream_candidate, "git", side_effect=raced):
            with self.assertRaisesRegex(ValueError, "changed during read"):
                self.inspect()


if __name__ == "__main__":
    unittest.main()
