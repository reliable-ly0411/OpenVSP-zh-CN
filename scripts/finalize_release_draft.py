#!/usr/bin/env python3
"""Replace an unpublished candidate only after exact-build desktop acceptance."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote
import zipfile

WORK = Path('draft-work')
REPO = os.environ['GITHUB_REPOSITORY']
TAG = os.environ['RELEASE_TAG']
SOURCE = os.environ['SOURCE_COMMIT']
OLD = os.environ['EXPECTED_DRAFT_SHA']
RUN = os.environ['BUILD_RUN_ID']


def gh(*args, output=None):
    result = subprocess.run(['gh', *args], check=True, stdout=output or subprocess.PIPE)
    return result.stdout


def api(path, method='GET', data=None):
    args = ['gh', 'api', f'repos/{REPO}/{path}', '--method', method]
    if data is not None:
        args += ['--input', '-']
    result = subprocess.run(args, input=json.dumps(data).encode() if data is not None else None,
                            check=True, stdout=subprocess.PIPE)
    return json.loads(result.stdout) if result.stdout else None


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(release):
    return {k: release[k] for k in ('id', 'tag_name', 'draft', 'prerelease')} | {
        'assets': sorted((a['id'], a['name'], a['digest']) for a in release['assets'])}


def find_release():
    # GitHub's by-tag REST endpoint excludes unpublished drafts.
    page = 1
    while True:
        releases = api(f'releases?per_page=100&page={page}')
        matches = [release for release in releases if release['tag_name'] == TAG]
        if len(matches) == 1:
            return matches[0]
        if matches or len(releases) < 100:
            raise ValueError('Missing or ambiguous release draft')
        page += 1


def download_asset(asset, destination):
    with destination.open('wb') as stream:
        gh('api', f'repos/{REPO}/releases/assets/{asset["id"]}',
           '--header', 'Accept: application/octet-stream', output=stream)


def guarded_draft():
    release = find_release()
    if not release['draft'] or not release['prerelease'] or release['tag_name'] != TAG:
        raise ValueError('Refusing to modify any published or non-prerelease release')
    ref = api(f'git/ref/tags/{TAG}')
    if ref['object']['type'] != 'commit' or ref['object']['sha'] != OLD:
        raise ValueError('Unpublished tag changed or is not the expected commit')
    return release


def prepare():
    release = guarded_draft()
    comparison = api(f'compare/{OLD}...{SOURCE}')
    if comparison['status'] not in ('ahead', 'identical'):
        raise ValueError('Candidate must fast-forward the unpublished tag')
    run = api(f'actions/runs/{RUN}')
    if run['head_sha'] != SOURCE or run['path'] != '.github/workflows/release-localized.yml':
        raise ValueError('Build source/workflow does not match acceptance')
    jobs = api(f'actions/runs/{RUN}/jobs?per_page=100')['jobs']
    for name in ('Build Windows 2022 x64', 'Build Linux Ubuntu 24.04 x86_64'):
        matches = [j for j in jobs if j['name'] == name]
        if len(matches) != 1 or matches[0]['conclusion'] != 'success':
            raise ValueError(f'Build job not successful: {name}')
    backup = WORK / 'backup'
    backup.mkdir(parents=True)
    (backup / 'release.json').write_text(json.dumps(release, indent=2))
    (backup / 'tag.json').write_text(json.dumps(api(f'git/ref/tags/{TAG}'), indent=2))
    expected_names = {f'OpenVSP-{TAG}-{p}.zip' for p in ('Ubuntu-24.04-x86_64', 'Windows-x64')} | {'SHA256SUMS.txt'}
    if {a['name'] for a in release['assets']} != expected_names:
        raise ValueError('Unexpected draft assets; refusing to replace')
    for asset in release['assets']:
        download_asset(asset, backup / asset['name'])
        if 'sha256:' + sha(backup / asset['name']) != asset['digest']:
            raise ValueError('Draft backup hash mismatch')
    output = WORK / 'accepted'
    output.mkdir()
    artifacts = api(f'actions/runs/{RUN}/artifacts?per_page=100')['artifacts']
    for name, platform, accepted in (
        ('localized-linux', 'Ubuntu-24.04-x86_64', os.environ['LINUX_SHA256']),
        ('localized-windows', 'Windows-x64', os.environ['WINDOWS_SHA256']),
    ):
        matches = [a for a in artifacts if a['name'] == name and not a['expired']]
        if len(matches) != 1:
            raise ValueError(f'Missing or ambiguous artifact: {name}')
        artifact = matches[0]
        outer = WORK / (name + '.zip')
        with outer.open('wb') as stream:
            gh('api', f'repos/{REPO}/actions/artifacts/{artifact["id"]}/zip', output=stream)
        if 'sha256:' + sha(outer) != artifact['digest']:
            raise ValueError('Artifact transport hash mismatch')
        filename = f'OpenVSP-{TAG}-{platform}.zip'
        with zipfile.ZipFile(outer) as archive:
            if archive.namelist() != [filename]:
                raise ValueError('Unexpected artifact contents')
            (output / filename).write_bytes(archive.read(filename))
        if sha(output / filename) != accepted:
            raise ValueError('Package differs from the desktop-accepted package')
    (output / 'SHA256SUMS.txt').write_text(''.join(
        f'{sha(p)}  {p.name}\n' for p in sorted(output.glob('*.zip'))))
    sys.path.insert(0, str(Path('source/scripts').resolve()))
    from release_notes import release_body, release_title, update_notes
    changes = update_notes(Path('source/README_zh-CN.md').read_text(), TAG)
    body = release_body(TAG, changes, REPO, SOURCE, RUN, prerelease=True)
    note = os.environ['VALIDATION_NOTE'].strip()
    if not note or len(note) > 6000:
        raise ValueError('Missing or excessive desktop acceptance note')
    body = body.replace('GUI 抽查范围以本次更新及发布页后续记录为准；自动构建成功不代表 GUI 全面验收。', note)
    (WORK / 'body.md').write_text(body)
    (WORK / 'title.txt').write_text(release_title(TAG, True))
    (WORK / 'plan.json').write_text(json.dumps(snapshot(release)))
    print('Draft backed up; build source and both accepted package hashes match')


def apply():
    release = guarded_draft()
    if json.loads(json.dumps(snapshot(release))) != json.loads((WORK / 'plan.json').read_text()):
        raise ValueError('Draft changed after backup')
    api(f'git/refs/tags/{TAG}', 'PATCH', {'sha': SOURCE, 'force': False})
    files = sorted((WORK / 'accepted').iterdir())
    for asset in release['assets']:
        api(f'releases/assets/{asset["id"]}', 'DELETE')
    upload_url = release['upload_url'].split('{')[0]
    for path in files:
        gh('api', upload_url + '?name=' + quote(path.name, safe=''), '--method', 'POST',
           '--header', 'Content-Type: application/octet-stream', '--input', str(path))
    check = WORK / 'downloaded'
    check.mkdir()
    uploaded = api(f'releases/{release["id"]}')
    for asset in uploaded['assets']:
        if asset['name'] not in {p.name for p in files}:
            raise ValueError('Unexpected uploaded asset name')
        download_asset(asset, check / asset['name'])
    if {p.name for p in check.iterdir()} != {p.name for p in files}:
        raise ValueError('Unexpected uploaded asset set')
    for p in files:
        if sha(p) != sha(check / p.name):
            raise ValueError('Uploaded asset download mismatch')
    final = api(f'releases/{release["id"]}')
    if not final['draft'] or final['id'] != release['id']:
        raise ValueError('Release changed before publication')
    if api(f'git/ref/tags/{TAG}')['object']['sha'] != SOURCE:
        raise ValueError('Tag changed before publication')
    api(f'releases/{release["id"]}', 'PATCH', {
        'name': (WORK / 'title.txt').read_text(), 'body': (WORK / 'body.md').read_text(),
        'draft': os.environ['PUBLISH'] != 'true', 'prerelease': True, 'make_latest': 'false',
    })
    print('Final package hashes and source tag verified; prerelease state applied')


if __name__ == '__main__':
    if not re.fullmatch(r'\d+\.\d+\.\d+-Codex-AI-zh-CN-r[1-9]\d*', TAG):
        raise ValueError('Only revision tags may be finalized')
    if any(not re.fullmatch(r'[0-9a-f]{40}', value) for value in (SOURCE, OLD)) or not RUN.isdigit():
        raise ValueError('Exact commits and numeric build run required')
    if any(not re.fullmatch(r'[0-9a-f]{64}', os.environ[k]) for k in ('LINUX_SHA256', 'WINDOWS_SHA256')):
        raise ValueError('Exact acceptance hashes required')
    {'prepare': prepare, 'apply': apply}[sys.argv[1]]()
