"""Offline notification, retention and compare-and-delete regression tests."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import upstream_maintenance as maintenance


class Client:
    repository = 'owner/repository'
    def __init__(self, issues=(), pulls=(), runs=None):
        self.issues, self.pulls, self.runs = list(issues), list(pulls), runs or {}
        self.writes = []
    def pages(self, path):
        return self.issues if path.startswith('issues?') else self.pulls
    def api(self, path, method='GET', data=None):
        if method == 'GET': return self.runs[path]
        self.writes.append((path, method, data))
        return dict(number=12)


def health(state='open', **extra):
    return dict(number=12, state=state, title=maintenance.TITLE, body=maintenance.MARKER,
                user=dict(login='github-actions[bot]'), **extra)


class NotifyTests(unittest.TestCase):
    def test_failure_plan_is_read_only_by_default(self):
        client = Client()
        result = maintenance.notify(client, 'failure', 'skipped', '', '123')
        self.assertEqual(result['action'], 'create'); self.assertFalse(result['applied'])
        self.assertEqual(client.writes, [])

    def test_failed_build_creates_one_assigned_issue(self):
        client = Client()
        maintenance.notify(client, 'success', 'failure', 'true', '123', True)
        self.assertEqual(len(client.writes), 1)
        path, method, data = client.writes[0]
        self.assertEqual((path, method, data['assignees']), ('issues', 'POST', ['owner']))
        self.assertIn('/actions/runs/123', data['body'])

    def test_repeat_failure_updates_and_recovery_closes_same_issue(self):
        client = Client([health()])
        maintenance.notify(client, 'failure', 'skipped', '', '123', True)
        self.assertEqual(client.writes[-1][:2], ('issues/12', 'PATCH'))
        self.assertEqual(client.writes[-1][2]['state'], 'open')
        maintenance.notify(client, 'success', 'skipped', 'false', '124', True)
        self.assertEqual(client.writes[-1][2]['state'], 'closed')
        self.assertEqual(client.writes[-1][2]['state_reason'], 'completed')

    def test_closed_issue_reopens_without_creating_duplicates(self):
        client = Client([health('closed')])
        maintenance.notify(client, 'success', 'cancelled', 'true', '125', True)
        self.assertEqual(client.writes[0][:2], ('issues/12', 'PATCH'))
        self.assertEqual(client.writes[0][2]['state'], 'open')

    def test_healthy_first_run_does_not_create_issue(self):
        client = Client()
        self.assertEqual(maintenance.notify(client, 'success', 'success', 'true', '123', True)['action'], 'none')
        self.assertEqual(client.writes, [])

    def test_duplicate_health_issues_fail_without_mutation(self):
        client = Client([health(), health()])
        with self.assertRaises(ValueError): maintenance.notify(client, 'failure', 'skipped', '', '123', True)
        self.assertEqual(client.writes, [])

    def test_user_issue_cannot_be_selected_for_update(self):
        item = health(); item['user'] = dict(login='owner')
        client = Client([item])
        maintenance.notify(client, 'success', 'skipped', 'false', '123', True)
        self.assertEqual(client.writes, [])

    def test_unknown_outcomes_and_non_numeric_run_id_fail_closed(self):
        for prepare, build, changed, run_id in [('failure', 'skipped', '', '../secrets'), ('unknown', 'success', 'true', '123')]:
            with self.assertRaises(ValueError): maintenance.notify(Client(), prepare, build, changed, run_id)
        self.assertTrue(maintenance.failure_state('success', 'failure', 'false'))
        self.assertTrue(maintenance.failure_state('success', 'skipped', ''))
        self.assertTrue(maintenance.failure_state('success', 'skipped', 'true'))
        self.assertFalse(maintenance.failure_state('success', 'skipped', 'false'))


class CleanupTests(unittest.TestCase):
    now = datetime(2026, 10, 20, tzinfo=timezone.utc)
    sha = 'a' * 40
    name = 'automation/upstream-123-1'
    def fixture(self, **updates):
        run = dict(path='.github/workflows/upstream-watch.yml', status='completed', run_attempt=1,
                   updated_at=(self.now - timedelta(days=8)).isoformat())
        run.update(updates)
        return Client(runs={'actions/runs/123': run})
    def git(self, *args, **kwargs):
        return subprocess.CompletedProcess(args, 0, f'{self.name} {self.sha}\n' if args[0] == 'for-each-ref' else '', '')

    def test_only_merged_old_candidate_without_open_pr_is_eligible(self):
        with patch.object(maintenance, 'git', self.git):
            plan = maintenance.candidate_plan(self.fixture(), self.now)
        self.assertEqual(len(plan), 1); self.assertTrue(plan[0]['eligible'])

    def test_grace_run_provenance_active_run_and_open_pr_are_preserved(self):
        cases = [self.fixture(updated_at=self.now.isoformat()), self.fixture(path='other.yml'),
                 self.fixture(status='in_progress'), self.fixture(run_attempt=0)]
        client = self.fixture(); client.pulls = [dict(head=dict(ref=self.name))]; cases.append(client)
        for client in cases:
            with self.subTest(client=client), patch.object(maintenance, 'git', self.git):
                self.assertFalse(maintenance.candidate_plan(client, self.now)[0]['eligible'])

    def test_unmerged_branch_is_never_deleted(self):
        def git(*args, **kwargs):
            return subprocess.CompletedProcess(args, 1 if args[0] == 'merge-base' else 0,
                    f'{self.name} {self.sha}\n' if args[0] == 'for-each-ref' else '', '')
        with patch.object(maintenance, 'git', git):
            self.assertEqual(maintenance.candidate_plan(self.fixture(), self.now)[0]['reason'], 'unmerged')

    def test_default_cleanup_only_records_plan(self):
        plan = [dict(branch=self.name, sha=self.sha, eligible=True)]
        with tempfile.TemporaryDirectory() as tmp, patch.object(maintenance, 'candidate_plan', return_value=plan), patch.object(maintenance, 'remove_candidate') as remove:
            output = Path(tmp) / 'record.json'
            maintenance.cleanup(self.fixture(), output)
            self.assertFalse(json.loads(output.read_text())[0]['deleted']); remove.assert_not_called()

    def test_new_open_pr_stops_apply_and_preserves_recovery_record(self):
        plan = [dict(branch=self.name, sha=self.sha, eligible=True)]
        client = self.fixture(); client.pulls = [dict(head=dict(ref=self.name))]
        with tempfile.TemporaryDirectory() as tmp, patch.object(maintenance, 'candidate_plan', return_value=plan), patch.object(maintenance, 'remove_candidate') as remove:
            output = Path(tmp) / 'record.json'
            maintenance.cleanup(client, output, True)
            self.assertEqual(json.loads(output.read_text())[0]['sha'], self.sha); remove.assert_not_called()

    def test_invalid_name_or_ineligible_entry_cannot_delete(self):
        for name, eligible in [('main', True), ('automation/upstream-123-1', False)]:
            with self.subTest(name=name), patch.object(maintenance, 'git') as git:
                with self.assertRaises(ValueError): maintenance.remove_candidate(dict(branch=name, sha=self.sha, eligible=eligible), 'fixture')
                git.assert_not_called()

    def test_real_refs_scanner_finds_candidate_branches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args, check=True, env=None):
                return subprocess.run(['git', *args], cwd=root, text=True, capture_output=True, check=check, env=env)
            git('init', '-b', 'main'); git('config', 'user.name', 'Retention test'); git('config', 'user.email', 'test@example.invalid')
            git('config', 'gc.autoDetach', 'false')
            (root / 'keep').write_text('source'); git('add', '.'); git('commit', '-m', 'first')
            sha = git('rev-parse', 'HEAD').stdout.strip()
            git('update-ref', 'refs/remotes/origin/main', sha)
            git('update-ref', 'refs/remotes/origin/' + self.name, sha)
            git('update-ref', 'refs/remotes/origin/automation/other', sha)
            with patch.object(maintenance, 'git', git):
                plan = maintenance.candidate_plan(self.fixture(), self.now)
            self.assertEqual([item['branch'] for item in plan], [self.name])
            self.assertEqual(plan[0]['sha'], sha)
            self.assertTrue(plan[0]['eligible'])

    def test_exact_sha_lease_rejects_concurrent_branch_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'; root.mkdir()
            remote = Path(tmp) / 'remote.git'
            def git(*args, check=True, env=None):
                return subprocess.run(['git', *args], cwd=root, text=True, capture_output=True, check=check, env=env)
            git('init', '-b', 'main'); git('config', 'user.name', 'Retention test'); git('config', 'user.email', 'test@example.invalid')
            git('config', 'gc.autoDetach', 'false')
            (root / 'keep').write_text('first'); git('add', '.'); git('commit', '-m', 'first')
            old = git('rev-parse', 'HEAD').stdout.strip()
            git('init', '--bare', str(remote)); git('--git-dir', str(remote), 'config', 'gc.autoDetach', 'false')
            git('remote', 'add', 'origin', str(remote)); git('push', 'origin', 'HEAD:main', f'HEAD:{self.name}')
            (root / 'keep').write_text('second'); git('commit', '-am', 'second')
            new = git('rev-parse', 'HEAD').stdout.strip(); git('push', 'origin', f'HEAD:{self.name}')
            with patch.object(maintenance, 'git', git):
                with self.assertRaises(subprocess.CalledProcessError):
                    maintenance.remove_candidate(dict(branch=self.name, sha=old, eligible=True), 'fixture')
            self.assertEqual(git('--git-dir', str(remote), 'rev-parse', self.name).stdout.strip(), new)
            self.assertEqual(git('--git-dir', str(remote), 'rev-parse', 'main').stdout.strip(), old)


if __name__ == '__main__': unittest.main()
