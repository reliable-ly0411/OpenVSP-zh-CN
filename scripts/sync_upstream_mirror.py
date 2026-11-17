#!/usr/bin/env python3
"""Refresh only the exact upstream-main mirror; never merge or force-push."""

import datetime
import json
import os
from pathlib import Path
import subprocess

UPSTREAM = 'https://github.com/OpenVSP/OpenVSP.git'
DESTINATION = 'https://github.com/reliable-ly0411/OpenVSP-zh-CN.git'
MIRROR = 'refs/heads/upstream-main'


def git(*args):
    # Never execute hooks, including when the caller supplies push credentials.
    return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', *args], text=True).strip()


def remote_sha(remote, ref):
    rows = git('ls-remote', '--refs', remote, ref).splitlines()
    if not rows:
        return None
    if len(rows) != 1 or rows[0].split()[1] != ref:
        raise RuntimeError(f'Unexpected remote ref: {ref}')
    return rows[0].split()[0]


def counts(base, head):
    """Match GitHub compare base...head: right-only is ahead, left-only behind."""
    behind, ahead = map(int, git('rev-list', '--left-right', '--count', f'{base}...{head}').split())
    return dict(ahead_by=ahead, behind_by=behind)


def sync(upstream=UPSTREAM, destination=DESTINATION):
    # URL arguments exist for offline repository tests, not as CLI/user inputs.
    if git('rev-parse', '--is-shallow-repository') != 'false':
        raise RuntimeError('Mirror synchronization requires full history')
    git('fetch', '--no-tags', upstream, 'refs/heads/main')
    target = git('rev-parse', '--verify', 'FETCH_HEAD^{commit}')
    before = remote_sha(destination, MIRROR)
    if before:
        git('fetch', '--no-tags', destination, MIRROR)
        if git('rev-parse', 'FETCH_HEAD') != before:
            raise RuntimeError('Mirror changed during fetch; retry with fresh refs')
        # Reject upstream rewinds, divergence and contaminated mirror history.
        git('merge-base', '--is-ancestor', before, target)
    git('fetch', '--no-tags', destination, 'refs/heads/main')
    localized = git('rev-parse', 'FETCH_HEAD')
    comparison = counts(target, localized)
    if before != target:
        # A normal push rejects concurrent non-fast-forward updates as well.
        git('push', destination, f'{target}:{MIRROR}')
    if remote_sha(destination, MIRROR) != target:
        raise RuntimeError('Mirror read-back does not match fetched upstream main')
    return dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                upstream=upstream, source_ref='refs/heads/main', mirror=MIRROR,
                before=before, after=target, localized_main=localized,
                action='unchanged' if before == target else 'created' if before is None else 'fast-forward',
                **comparison)


def main():
    result = sync()
    record = json.dumps(result, ensure_ascii=False, indent=2)
    print(record)
    if summary := os.environ.get('GITHUB_STEP_SUMMARY'):
        with Path(summary).open('a', encoding='utf-8') as handle:
            handle.write('\n### Exact upstream mirror and main comparison\n\n```json\n' + record + '\n```\n')


if __name__ == '__main__':
    main()
