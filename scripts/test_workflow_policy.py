"""Keep credential boundaries and opt-in maintenance explicit in workflow text."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WorkflowPolicyTests(unittest.TestCase):
    def test_every_external_action_uses_full_commit_sha(self):
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            for action in re.findall(r'\buses:\s*([^\s#]+)', path.read_text()):
                if not action.startswith('./'):
                    with self.subTest(path=path.name, action=action):
                        self.assertRegex(action, r'^[\w./-]+@[0-9a-f]{40}$')

    def test_legacy_build_is_explicitly_read_only(self):
        text = (ROOT / '.github/workflows/build.yml').read_text()
        self.assertIn('\npermissions:\n  contents: read\n', text)
        self.assertIn('persist-credentials: false', text)

    def test_merged_tree_cannot_supply_privileged_maintenance_code(self):
        text = (ROOT / '.github/workflows/prepare-upstream-update.yml').read_text()
        self.assertIn('persist-credentials: false', text)
        self.assertLess(text.index('Snapshot trusted maintenance tools'), text.index('Prepare upstream merge'))
        self.assertIn('python3 -I "$RUNNER_TEMP/openvsp-maintenance/check_localization_release.py" --source "$GITHUB_WORKSPACE"', text)
        self.assertNotIn('python3 scripts/', text)
        self.assertEqual(text.count('PUSH_TOKEN:'), 1)
        self.assertLess(text.index('Check and commit candidate without write credentials'), text.index('PUSH_TOKEN:'))
        self.assertIn('GIT_CONFIG_KEY_1=core.hooksPath', text)
        self.assertNotIn('refs/heads/main', text)

    def test_notification_and_cleanup_are_opt_in_and_separate(self):
        text = (ROOT / '.github/workflows/upstream-watch.yml').read_text()
        self.assertIn("vars.OPENVSP_NOTIFY_UPSTREAM_FAILURES == 'true'", text)
        self.assertIn("vars.OPENVSP_CLEAN_MERGED_CANDIDATES == 'true'", text)
        self.assertIn('cleanup --output candidate-retention-plan.json', text)
        self.assertIn('notify --apply', text)
        self.assertIn('cleanup --apply --output candidate-cleanup-record.json', text)
        self.assertIn('retention-days: 90', text)
        self.assertNotIn('native-promote', text)

    def test_backfill_checks_untracked_source_and_builds_tests_outside_source(self):
        text = (ROOT / 'scripts/backfill_build.sh').read_text()
        self.assertIn('python "$TOOLS/check_source_worktree.py" "$SOURCE"', text)
        self.assertIn('-B "$ROOT/localization-tests"', text)
        self.assertNotIn('-B localization-tests\n', text)
        native = (ROOT / 'scripts/native_verify.py').read_text()
        self.assertIn('worktree_clean = require_clean_source(source)', native)
        self.assertIn('source_worktree_clean=worktree_clean', native)


if __name__ == '__main__': unittest.main()
