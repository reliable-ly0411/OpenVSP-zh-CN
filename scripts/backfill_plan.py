#!/usr/bin/env python3
"""Immutable historical build plan. This workflow never writes to Releases."""
import json
import os
import subprocess
from pathlib import Path

RELEASES = (
    ('3.51.2', '3.51.2-Codex-AI-zh-CN-r7', '24f270c1ffc52e7477b2305669172ba49b49b114'),
    ('3.51.3', '3.51.3-Codex-AI-zh-CN-r2', '4b523612b030d8d087dba49f79a716712496c403'),
    ('3.53.0', '3.53.0-Codex-AI-zh-CN', '6509db13cad1b2aabdc87f48bbfa1b287f117311'),
    ('3.54.0', '3.54.0-Codex-AI-zh-CN-r1', 'c96c808290718a2c9376a8f351a4a0146f38cba9'),
    ('3.55.0', '3.55.0-Codex-AI-zh-CN-auto.5240ef210f41', 'b12bc821b5ee256a3d8f38dc336ce5cb14efe53b'),
)
PLATFORMS = (
    dict(platform='macOS-14-arm64-Python3.11', runner='macos-14', arch='arm64', llvm='18', python='3.11'),
    dict(platform='macOS-15-x86_64-Python3.11', runner='macos-15-intel', arch='x86_64', llvm='16', python='3.11'),
    dict(platform='Ubuntu-24.04_arm64-Python3.12', runner='ubuntu-24.04-arm', arch='aarch64', llvm='', python='3.12'),
)

def matrix(scope):
    if scope not in ('pilot', 'all'):
        raise ValueError('Unknown scope')
    return {'include': [dict(version=v, tag=t, sha=s, **p) for v,t,s in RELEASES
                        if scope == 'all' or v == '3.53.0' for p in PLATFORMS]}

def validate_pilot(run, jobs, repository):
    if (run.get('conclusion') != 'success' or run.get('status') != 'completed'
            or run.get('repository', {}).get('full_name') != repository
            or run.get('path') != '.github/workflows/backfill-platforms.yml'):
        raise ValueError('Pilot must be a successful run of this repository/workflow')
    expected = {f"3.53.0 / {p['platform']}" for p in PLATFORMS}
    actual = {j['name'] for j in jobs if j.get('conclusion') == 'success'}
    if not expected.issubset(actual):
        raise ValueError('All three pilot platform jobs must have succeeded')
    # Do not accept an older, unrelated implementation as proof for new build tooling.
    parent = run['head_sha']
    if subprocess.run(['git', 'merge-base', '--is-ancestor', parent, 'HEAD']).returncode:
        raise ValueError('Pilot commit must be in current history; use a main-branch pilot after squash merge')
    changed = subprocess.check_output(['git', 'diff', '--name-only', parent, 'HEAD', '--',
                                      'scripts/backfill_*', '.github/workflows/backfill-platforms.yml'], text=True)
    if changed.strip():
        raise ValueError('Build tooling changed since pilot; repeat pilot before all')

def main():
    scope = os.environ.get('SCOPE', 'pilot')
    if scope == 'all':
        run_id = os.environ.get('PILOT_RUN_ID', '')
        if not run_id.isdecimal():
            raise ValueError('Provide the successful pilot run ID')
        repo = os.environ['GITHUB_REPOSITORY']
        def api(path):
            return json.loads(subprocess.check_output(['gh', 'api', path], text=True))
        run = api(f'repos/{repo}/actions/runs/{run_id}')
        jobs = api(f'repos/{repo}/actions/runs/{run_id}/jobs?per_page=100')['jobs']
        # Fetch only the known GitHub Actions head commit for ancestry validation.
        subprocess.run(['git', 'fetch', '--no-tags', '--unshallow', 'origin'], check=True)
        subprocess.run(['git', 'fetch', '--no-tags', 'origin', run['head_sha']], check=True)
        validate_pilot(run, jobs, repo)
    output = json.dumps(matrix(scope), separators=(',', ':'))
    with Path(os.environ['GITHUB_OUTPUT']).open('a') as f:
        f.write('matrix=' + output + '\n')
    print(f'Planned {len(matrix(scope)["include"])} native builds; no Release write permissions')

if __name__ == '__main__':
    main()
