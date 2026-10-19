"""Keep legacy-family candidate checks lightweight and public writes retired."""
from pathlib import Path
import unittest


WORKFLOWS = Path(__file__).resolve().parents[1] / '.github/workflows'


class CandidateWorkflowIsolationTests(unittest.TestCase):
    def assert_read_only(self, workflow):
        self.assertIn('permissions:\n  contents: read\n', workflow)
        self.assertNotIn('contents: write', workflow)
        self.assertNotIn('issues: write', workflow)
        self.assertNotIn('pull-requests: write', workflow)
        self.assertNotIn('gh release ', workflow)
        self.assertNotIn('git push ', workflow)

    def test_candidate_pr_is_lightweight_and_has_real_test_targets(self):
        workflow = (WORKFLOWS / 'build-localized-pr.yml').read_text(encoding='utf-8')
        self.assertIn("branches: [main, 'develop/**', 'dev/**']", workflow)
        self.assert_read_only(workflow)
        self.assertNotIn('release-localized.yml', workflow)
        self.assertNotIn('--target package', workflow)
        self.assertNotIn('backfill_test.py', workflow)
        self.assertIn("python3 -m unittest discover -s scripts -p 'test_*.py' -v", workflow)
        self.assertIn('cmake -S scripts/localization_tests', workflow)
        self.assertIn('-DVSP_TEST_XML_TEXT=ON', workflow)

    def test_legacy_release_is_reusable_build_only(self):
        workflow = (WORKFLOWS / 'release-localized.yml').read_text(encoding='utf-8')
        events = workflow.split('\non:\n', 1)[1].split('\npermissions:\n', 1)[0]
        self.assert_read_only(workflow)
        self.assertIn('  workflow_call:', events)
        for event in ('push', 'release', 'pull_request', 'schedule', 'workflow_dispatch'):
            self.assertNotRegex(events, rf'(?m)^  {event}:')
        self.assertNotRegex(workflow, r'(?m)^  (publish|promote|release):')
        self.assertNotIn('publish:', events)

    def test_legacy_upstream_entry_only_displays_migration_notice(self):
        workflow = (WORKFLOWS / 'upstream-watch.yml').read_text(encoding='utf-8')
        events = workflow.split('\non:\n', 1)[1].split('\npermissions:\n', 1)[0]
        self.assert_read_only(workflow)
        self.assertIn('  workflow_dispatch:', events)
        for event in ('push', 'release', 'pull_request', 'schedule', 'workflow_call'):
            self.assertNotRegex(events, rf'(?m)^  {event}:')
        self.assertNotIn('uses:', workflow)
        self.assertNotRegex(workflow, r'(?m)^  (prepare|build|publish|promote):')
        self.assertIn('default branch', workflow)

    def test_legacy_transplant_only_displays_migration_notice(self):
        workflow = (WORKFLOWS / 'prepare-upstream-update.yml').read_text(encoding='utf-8')
        events = workflow.split('\non:\n', 1)[1].split('\npermissions:\n', 1)[0]
        self.assert_read_only(workflow)
        self.assertIn('  workflow_dispatch:', events)
        for event in ('push', 'release', 'pull_request', 'schedule', 'workflow_call'):
            self.assertNotRegex(events, rf'(?m)^  {event}:')
        self.assertNotIn('uses:', workflow)
        self.assertNotRegex(workflow, r'(?m)^  (prepare|build|publish|promote):')
        self.assertIn('default branch', workflow)


if __name__ == '__main__':
    unittest.main()
