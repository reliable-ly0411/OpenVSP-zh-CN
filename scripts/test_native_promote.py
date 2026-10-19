"""Read-only artifact provenance, review identity and extraction regression tests."""
from pathlib import Path
import tempfile
import unittest
import zipfile

from native_plan import PLATFORMS
from native_promote import (artifact_record, extract_artifact, latest_jobs, paginated,
                            validate_evidence, validate_jobs, validate_run)
import test_native_release as fixtures
from test_native_release import SOURCE, TAG, WORKFLOW
from backfill_verify import digest
import json


class PromotionTests(unittest.TestCase):
    def test_run_must_be_successful_same_repository_exact_workflow(self):
        run = dict(repository={'full_name':'example/repo'}, path='.github/workflows/native-prerelease.yml',
                   event='workflow_dispatch', status='completed', conclusion='success', head_sha=WORKFLOW)
        self.assertEqual(validate_run(run, [], 'example/repo'), WORKFLOW)
        for key, value in [('event', 'pull_request'), ('conclusion', 'failure'), ('status', 'in_progress'),
                           ('path', '.github/workflows/other.yml'), ('head_sha', 'main')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_run(dict(run, **{key:value}), [], 'example/repo')
        with self.assertRaises(ValueError): validate_run(run, [], 'other/repo')

    def test_every_native_job_and_assembly_must_succeed(self):
        names = [f'3.55.0 / {p["platform"]}' for p in PLATFORMS] + ['regression', 'plan', 'assemble']
        jobs = [dict(name=name, status='completed', conclusion='success') for name in names]
        validate_jobs(jobs, '3.55.0')
        for bad in (jobs[:-1], jobs + [jobs[0]], [dict(jobs[0], conclusion='skipped')] + jobs[1:]):
            with self.assertRaises(ValueError): validate_jobs(bad, '3.55.0')
        with self.assertRaises(ValueError):
            validate_jobs([dict(jobs[0], status='in_progress')] + jobs[1:], '3.55.0')

    def jobs(self):
        names = [f'3.55.0 / {p["platform"]}' for p in PLATFORMS] + ['regression', 'plan', 'assemble']
        return [dict(id=index + 1, name=name, status='completed', conclusion='success',
                     run_id=123, head_sha=WORKFLOW, run_attempt=1)
                for index, name in enumerate(names)]

    def test_selective_retry_preserves_earlier_successful_jobs(self):
        jobs = self.jobs()
        jobs[3]['conclusion'] = 'failure'
        retry = dict(jobs[3], id=103, run_attempt=2, conclusion='success')
        selected = latest_jobs(jobs + [retry], '123', WORKFLOW, 2)
        validate_jobs(selected, '3.55.0')
        self.assertEqual(len(selected), len(jobs))
        self.assertIn(retry, selected)
        self.assertIn(jobs[0], selected)
        self.assertNotIn(jobs[3], selected)
        self.assertEqual(latest_jobs(list(reversed(jobs + [retry])), 123, WORKFLOW, 2), selected)

    def test_latest_failure_cannot_reuse_earlier_success(self):
        jobs = self.jobs()
        for conclusion in ('failure', 'cancelled', 'skipped', None):
            with self.subTest(conclusion=conclusion), self.assertRaises(ValueError):
                retry = dict(jobs[0], id=100, run_attempt=2, conclusion=conclusion)
                validate_jobs(latest_jobs(jobs + [retry], 123, WORKFLOW, 2), '3.55.0')

    def test_job_history_rejects_other_runs_or_workflows(self):
        jobs = self.jobs()
        for changes in ({'run_id': 456}, {'head_sha': 'c' * 40}, {'head_sha': None}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                latest_jobs([dict(jobs[0], **changes)] + jobs[1:], 123, WORKFLOW, 1)

    def test_attempt_metadata_must_be_complete_and_bounded(self):
        jobs = self.jobs()
        for attempt in (None, 0, -1, True, '1', 2):
            with self.subTest(attempt=attempt), self.assertRaises(ValueError):
                latest_jobs([dict(jobs[0], run_attempt=attempt)] + jobs[1:], 123, WORKFLOW, 1)
        for run_attempt in (None, 0, True, '1', 2):
            with self.subTest(run_attempt=run_attempt), self.assertRaises(ValueError):
                latest_jobs(jobs, 123, WORKFLOW, run_attempt)

    def test_duplicate_or_missing_job_identity_fails(self):
        jobs = self.jobs()
        for bad in (jobs + [dict(jobs[0], id=100)],
                    jobs + [dict(jobs[0], name='different')],
                    [dict(jobs[0], id=None)] + jobs[1:],
                    [dict(jobs[0], name='')] + jobs[1:]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                latest_jobs(bad, 123, WORKFLOW, 1)
        with self.assertRaises(ValueError):
            validate_jobs(latest_jobs(jobs[:-1], 123, WORKFLOW, 1), '3.55.0')

    def test_all_attempt_filter_survives_pagination(self):
        calls = []
        def api(path):
            calls.append(path)
            return {'jobs': list(range(100)) if len(calls) == 1 else [100]}
        self.assertEqual(paginated(api, 'actions/runs/123/jobs?filter=all', 'jobs'), list(range(101)))
        self.assertEqual(calls, ['actions/runs/123/jobs?filter=all&per_page=100&page=1',
                                 'actions/runs/123/jobs?filter=all&per_page=100&page=2'])

    def test_artifact_must_be_unique_unexpired_and_have_transport_digest(self):
        artifact = dict(name='native-release-assets', expired=False, digest='sha256:' + 'a'*64)
        self.assertEqual(artifact_record([artifact], artifact['name']), artifact)
        for rows in ([], [artifact, artifact], [dict(artifact, expired=True)], [dict(artifact, digest=None)]):
            with self.assertRaises(ValueError):
                artifact_record(rows, artifact['name'])

    def test_only_exact_flat_safe_artifact_names_are_extracted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index, name in enumerate(('allowed.zip', '../allowed.zip', 'sub/allowed.zip')):
                archive = root / f'{index}.zip'
                with zipfile.ZipFile(archive, 'w') as z: z.writestr(name, b'inert bytes')
                if index == 0:
                    extract_artifact(archive, root / 'valid', {'allowed.zip'})
                    self.assertEqual((root / 'valid/allowed.zip').read_bytes(), b'inert bytes')
                else:
                    with self.assertRaises(ValueError): extract_artifact(archive, root / f'bad{index}', {name})

    def test_original_evidence_binds_source_run_tooling_manifest_and_all_packages(self):
        fixture = fixtures.NativeReleaseTests(); fixture.setUp()
        try:
            fixture.prepare()
            evidence = dict(schema=1, source_sha=SOURCE, tag=TAG, run_id='123', workflow_sha=WORKFLOW,
                            manifest_sha256=digest(fixture.output / 'SHA256SUMS.txt'),
                            reports=[json.loads(p.read_text()) for p in fixture.artifacts.rglob('verification.json')])
            validate_evidence(evidence, fixture.output, SOURCE, TAG, '123', WORKFLOW)
            for key, value in [('source_sha', 'c'*40), ('run_id','456'), ('workflow_sha','d'*40),
                               ('manifest_sha256','e'*64), ('reports', evidence['reports'][:-1])]:
                with self.subTest(key=key), self.assertRaises(ValueError):
                    validate_evidence(dict(evidence, **{key:value}), fixture.output, SOURCE, TAG, '123', WORKFLOW)
        finally:
            fixture.doCleanups()


if __name__ == '__main__':
    unittest.main()
