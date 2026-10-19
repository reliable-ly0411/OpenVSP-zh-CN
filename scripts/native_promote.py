#!/usr/bin/env python3
"""Promote the original, GUI-reviewed artifact bytes without rebuilding anything."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from backfill_verify import digest
from native_plan import PLATFORMS, asset_name, validate_inputs
from native_release import GitHub, publish, validate_gui_review, validate_report, verify_manifest


def paginated(api, path, key):
    rows, page = [], 1
    separator = '&' if '?' in path else '?'
    while True:
        result = api(f'{path}{separator}per_page=100&page={page}')[key]
        rows.extend(result)
        if len(result) < 100:
            return rows
        page += 1


def validate_run(run, jobs, repository):
    if (run.get('repository', {}).get('full_name') != repository
            or run.get('path') != '.github/workflows/native-prerelease.yml'
            or run.get('event') != 'workflow_dispatch'
            or run.get('status') != 'completed' or run.get('conclusion') != 'success'
            or not re.fullmatch(r'[0-9a-f]{40}', run.get('head_sha', ''))):
        raise ValueError('Original build must be a completed successful native prerelease run in this repository')
    return run['head_sha']


def latest_jobs(jobs, run_id, workflow_sha, run_attempt):
    """Keep each named job's latest attempt, including successful non-rerun jobs."""
    if type(run_attempt) is not int or run_attempt < 1:
        raise ValueError('Original build has no valid run attempt')
    selected, identities, job_ids = {}, set(), set()
    for job in jobs:
        name, attempt, job_id = job.get('name'), job.get('run_attempt'), job.get('id')
        if (not isinstance(name, str) or not name
                or type(attempt) is not int or not 1 <= attempt <= run_attempt
                or type(job_id) is not int or job_id < 1
                or str(job.get('run_id')) != str(run_id)
                or job.get('head_sha') != workflow_sha):
            raise ValueError('Job provenance differs from the original build')
        identity = (name, attempt)
        if identity in identities or job_id in job_ids:
            raise ValueError('Duplicate job identity in original build history')
        identities.add(identity)
        job_ids.add(job_id)
        if name not in selected or attempt > selected[name]['run_attempt']:
            selected[name] = job
    if not any(job['run_attempt'] == run_attempt for job in selected.values()):
        raise ValueError('Original build job history is missing its latest attempt')
    return [selected[name] for name in sorted(selected)]


def validate_jobs(jobs, version):
    expected = {f'{version} / {p["platform"]}' for p in PLATFORMS} | {'regression', 'plan', 'assemble'}
    for name in expected:
        matching = [job for job in jobs if job.get('name') == name]
        if (len(matching) != 1 or matching[0].get('status') != 'completed'
                or matching[0].get('conclusion') != 'success'):
            raise ValueError('Original native job is missing, duplicated or unsuccessful: ' + name)


def artifact_record(artifacts, name):
    found = [a for a in artifacts if a.get('name') == name and not a.get('expired')]
    if len(found) != 1 or not re.fullmatch(r'sha256:[0-9a-f]{64}', (found[0].get('digest') or '')):
        raise ValueError('Missing, expired, ambiguous or unverifiable artifact: ' + name)
    return found[0]


def extract_artifact(archive, destination, expected_names):
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        files = [i for i in z.infolist() if not i.is_dir()]
        names = [i.filename for i in files]
        if len(names) != len(set(names)) or set(names) != set(expected_names):
            raise ValueError('Artifact contents do not match the exact expected filenames')
        for info in files:
            if '/' in info.filename or '\\' in info.filename or info.filename in ('.', '..'):
                raise ValueError('Unsafe artifact filename')
            with z.open(info) as source, (destination / info.filename).open('wb') as target:
                shutil.copyfileobj(source, target)
        if z.testzip():
            raise ValueError('Artifact ZIP CRC failed')


def validate_evidence(evidence, directory, source_sha, tag, run_id, workflow_sha):
    version = validate_inputs(source_sha, tag)
    exact = dict(schema=1, source_sha=source_sha, tag=tag, run_id=str(run_id), workflow_sha=workflow_sha,
                 manifest_sha256=digest(directory / 'SHA256SUMS.txt'))
    if any(evidence.get(k) != value for k, value in exact.items()):
        raise ValueError('Original build evidence identity or manifest mismatch')
    reports = evidence.get('reports', [])
    if len(reports) != len(PLATFORMS):
        raise ValueError('Evidence must include all five native reports')
    seen = set()
    for report in reports:
        package = directory / asset_name(version, report.get('platform'))
        native_platform = validate_report(report, package, source_sha, tag, run_id, workflow_sha)
        if native_platform in seen:
            raise ValueError('Duplicate native report in original evidence')
        seen.add(native_platform)
    verify_manifest(directory, version)


def download_artifact(client, artifact, path):
    with path.open('wb') as target:
        subprocess.run(['gh', 'api', f'repos/{client.repository}/actions/artifacts/{artifact["id"]}/zip'],
                       check=True, stdout=target)
    if 'sha256:' + digest(path) != artifact['digest']:
        raise ValueError('Artifact transport digest mismatch')


def main():
    source, tag = os.environ['SOURCE_SHA'], os.environ['NEW_TAG']
    version = validate_inputs(source, tag)
    run_id = os.environ['BUILD_RUN_ID']
    if not run_id.isdecimal():
        raise ValueError('build_run_id must be numeric')
    client = GitHub(os.environ['GITHUB_REPOSITORY'])
    run = client.api(f'actions/runs/{run_id}')
    # GitHub's default filter=latest can omit earlier successful jobs when only
    # failed jobs were rerun. Read all history, but never fall back from a later
    # unsuccessful attempt to an earlier success.
    history = paginated(client.api, f'actions/runs/{run_id}/jobs?filter=all', 'jobs')
    workflow_sha = validate_run(run, history, client.repository)
    jobs = latest_jobs(history, run_id, workflow_sha, run.get('run_attempt'))
    validate_jobs(jobs, version)
    artifacts = paginated(client.api, f'actions/runs/{run_id}/artifacts', 'artifacts')
    workspace = Path('promotion-work'); workspace.mkdir()
    directory = workspace / 'public-assets'
    expected = {asset_name(version, p['platform']) for p in PLATFORMS} | {'SHA256SUMS.txt'}
    for name, destination, names in (
        ('native-release-assets', directory, expected),
        ('native-release-evidence', workspace / 'evidence', {'release-evidence.json'}),
    ):
        artifact = artifact_record(artifacts, name)
        archive = workspace / (name + '.zip')
        download_artifact(client, artifact, archive)
        extract_artifact(archive, destination, names)
    evidence = json.loads((workspace / 'evidence/release-evidence.json').read_text(encoding='utf-8'))
    validate_evidence(evidence, directory, source, tag, run_id, workflow_sha)
    review = dict(manifest_sha256=os.environ['MANIFEST_SHA256'], linux_gui_sha256=os.environ['LINUX_GUI_SHA256'],
                  validation_note=os.environ['VALIDATION_NOTE'])
    validate_gui_review(directory, version, review)
    # User-provided review details remain CI-only, separate from public assets.
    record = dict(source_sha=source, tag=tag, build_run_id=run_id, workflow_sha=workflow_sha,
                  build_jobs=[dict(name=job['name'], id=job['id'], run_attempt=job['run_attempt'])
                              for job in jobs], **review)
    Path('gui-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    result = publish(client, directory, source, tag, review=review)
    print('Original reviewed artifacts published without rebuilding: ' + result['html_url'])


if __name__ == '__main__':
    main()
