#!/usr/bin/env python3
"""Add-only draft recovery and read-back verification for a NEW native prerelease.

Never move tags, delete assets, overwrite assets, or edit a published Release.
A failed upload leaves a resumable unpublished draft; rerun with the same bytes.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import quote
import zipfile

from backfill_verify import digest
from native_plan import PLATFORMS, REQUIRED_CHECKS, asset_name, validate_inputs


def validate_report(report, package, source_sha, tag, run_id, workflow_sha):
    version = validate_inputs(source_sha, tag)
    native_platform = report.get('platform')
    target = next((p for p in PLATFORMS if p['platform'] == native_platform), None)
    if target is None:
        raise ValueError('Unknown native platform report')
    exact = dict(schema=2, tag=tag, source_sha=source_sha, version=version,
                 platform=native_platform, architecture=target['arch'], python=target['python'],
                 workflow_sha=workflow_sha, run_id=str(run_id), archive=asset_name(version, native_platform),
                 source_tracked_files_clean=True)
    if any(report.get(k) != value for k, value in exact.items()):
        raise ValueError('Verification report source/platform/run does not match')
    if set(report.get('checks', [])) != REQUIRED_CHECKS:
        raise ValueError('Required native checks are missing or unknown')
    if report.get('requirements_install', {}).get('numpy') != '1.26.4':
        raise ValueError('Fresh runtime NumPy ABI was not verified')
    if not package.is_file() or package.stat().st_size != report.get('bytes') or digest(package) != report.get('sha256'):
        raise ValueError('Package bytes differ from native verification report')
    with zipfile.ZipFile(package) as archive:
        if archive.testzip():
            raise ValueError('Package ZIP integrity failed')
    return native_platform


def prepare_assets(artifacts, output, source_sha, tag, run_id, workflow_sha):
    version = validate_inputs(source_sha, tag)
    reports = list(artifacts.rglob('verification.json'))
    if len(reports) != len(PLATFORMS):
        raise ValueError('All five native verification reports are required')
    selected = {}
    for path in reports:
        report = json.loads(path.read_text(encoding='utf-8'))
        # Derive the filename from the validated platform, never a path in JSON.
        package = path.parent / asset_name(version, report.get('platform'))
        native_platform = validate_report(report, package, source_sha, tag, run_id, workflow_sha)
        if native_platform in selected:
            raise ValueError('Duplicate native platform report')
        selected[native_platform] = package
    if {p.resolve() for p in artifacts.rglob('*.zip')} != {p.resolve() for p in selected.values()}:
        raise ValueError('Unexpected or missing ZIP artifact')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Refusing to replace a populated release staging directory')
    output.mkdir(parents=True, exist_ok=True)
    for package in selected.values():
        shutil.copyfile(package, output / package.name)
    manifest = ''.join(f'{digest(path)}  {path.name}\n' for path in sorted(output.glob('*.zip')))
    (output / 'SHA256SUMS.txt').write_text(manifest, encoding='utf-8')
    verify_manifest(output, version)
    return selected


def verify_manifest(directory, version):
    expected = {asset_name(version, p['platform']) for p in PLATFORMS}
    if {p.name for p in directory.iterdir()} != expected | {'SHA256SUMS.txt'}:
        raise ValueError('Public assets must be exactly five ZIPs and SHA256SUMS.txt')
    sums = {}
    for line in (directory / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  ([^/\\]+\.zip)', line)
        if not match or match[2] in sums:
            raise ValueError('Noncanonical or duplicate checksum entry')
        sums[match[2]] = match[1]
    if set(sums) != expected:
        raise ValueError('Checksum manifest must cover every published ZIP exactly once')
    for name, checksum in sums.items():
        if digest(directory / name) != checksum:
            raise ValueError('Package checksum mismatch: ' + name)
    return sums


def find_release(api, tag):
    matches, page = [], 1
    while True:
        rows = api(f'releases?per_page=100&page={page}')
        matches.extend(r for r in rows if r.get('tag_name') == tag)
        if len(rows) < 100:
            break
        page += 1
    if len(matches) > 1:
        raise ValueError('Multiple releases use this tag; refusing ambiguous recovery')
    return matches[0] if matches else None


def release_body(tag, source_sha, repository, linux_gui_reviewed=False):
    version = validate_inputs(source_sha, tag)
    gui = ('Linux AMD64 主界面、机翼页及模型名称/路径回归已人工抽查；其他平台 GUI 未作人工验收声明。'
           if linux_gui_reviewed else 'GUI 截图待目视复核，不代表全面 GUI 验收。')
    return (f'OpenVSP {version} 非官方简体中文预发布。修复界面本地化、模型名称保存、运行资源布局与 Python 依赖兼容问题。\n\n'
            '提供 Ubuntu 24.04 AMD64/ARM64、Windows x64、macOS 14 ARM64 与 macOS 15 Intel 五个平台包；'
            '请按 SHA256SUMS.txt 校验后解压。Linux 需中文字体；macOS 使用本地 ad-hoc 签名，尚未公证。'
            f'{gui}\n\n'
            f'[使用说明与验证范围](https://github.com/{repository}/blob/{source_sha}/README_zh-CN.md)。'
            'OpenVSP 原软件版权、作者归属及 NOSA 1.3 许可不变。')


class GitHub:
    def __init__(self, repository):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('Invalid repository')
        self.repository = repository

    def api(self, path, method='GET', data=None, missing=False):
        result = subprocess.run(['gh', 'api', f'repos/{self.repository}/{path}', '--method', method,
                                 *(['--input', '-'] if data is not None else [])],
                                input=json.dumps(data).encode() if data is not None else None,
                                capture_output=True)
        if result.returncode:
            if missing and b'HTTP 404' in result.stderr:
                return None
            raise RuntimeError(f'GitHub {method} {path} failed; no destructive recovery attempted')
        return json.loads(result.stdout) if result.stdout else None

    def upload(self, release, path):
        url = release['upload_url'].split('{')[0]
        prefix = f'https://uploads.github.com/repos/{self.repository}/releases/'
        if not url.startswith(prefix):
            raise ValueError('Unexpected GitHub upload destination')
        subprocess.run(['gh', 'api', url + '?name=' + quote(path.name, safe=''), '--method', 'POST',
                        '--header', 'Content-Type: application/octet-stream', '--input', str(path)],
                       check=True, stdout=subprocess.DEVNULL)

    def download(self, asset, path):
        with path.open('wb') as output:
            subprocess.run(['gh', 'api', f'repos/{self.repository}/releases/assets/{asset["id"]}',
                            '--header', 'Accept: application/octet-stream'], check=True, stdout=output)


def validate_gui_review(directory, version, review):
    if not isinstance(review, dict):
        raise ValueError('A hash-bound Linux GUI review is required before publication')
    for key, path in (
            ('manifest_sha256', directory / 'SHA256SUMS.txt'),
            ('linux_gui_sha256', directory / asset_name(version, 'Ubuntu-24.04_amd64'))):
        if not re.fullmatch(r'[0-9a-f]{64}', review.get(key, '')) or review[key] != digest(path):
            raise ValueError('GUI acceptance hash does not match the exact original build')
    note = review.get('validation_note', '').strip()
    if not note or len(note) > 6000:
        raise ValueError('A concise actual Linux GUI review note is required')


def publish(client, directory, source_sha, tag, review=None):
    version = validate_inputs(source_sha, tag)
    verify_manifest(directory, version)
    validate_gui_review(directory, version, review)
    files = {p.name: p for p in directory.iterdir()}
    release = find_release(client.api, tag)
    if release and (not release.get('draft') or not release.get('prerelease')):
        raise ValueError('Published or non-prerelease release is immutable')
    ref_path = 'git/ref/tags/' + quote(tag, safe='')
    ref = client.api(ref_path, missing=True)
    if ref is not None:
        if ref['object'].get('type') != 'commit' or ref['object'].get('sha') != source_sha:
            raise ValueError('Existing tag does not match the exact source')
    else:
        if release:
            raise ValueError('Existing draft has lost its source tag')
        client.api('git/refs', 'POST', {'ref': 'refs/tags/' + tag, 'sha': source_sha})
    title = f'OpenVSP {version} 简体中文版（RC {tag.rsplit(".", 1)[1]}）'
    body = release_body(tag, source_sha, client.repository, linux_gui_reviewed=True)
    if release is None:
        release = client.api('releases', 'POST', dict(tag_name=tag, target_commitish=source_sha,
                                                     name=title, body=body, draft=True,
                                                     prerelease=True, make_latest='false'))
    def guarded():
        current = client.api(f'releases/{release["id"]}')
        ref_now = client.api(ref_path)
        if (not current.get('draft') or not current.get('prerelease') or current.get('tag_name') != tag
                or current.get('target_commitish') != source_sha
                or ref_now.get('object', {}).get('type') != 'commit'
                or ref_now.get('object', {}).get('sha') != source_sha):
            raise ValueError('Draft/source identity changed; refusing further mutations')
        return current
    with tempfile.TemporaryDirectory(prefix='native-release-readback-') as temp:
        checked = Path(temp)
        current = guarded()
        names = [asset['name'] for asset in current['assets']]
        if len(names) != len(set(names)) or set(names) - files.keys():
            raise ValueError('Unexpected or duplicate draft assets; never delete or replace')
        # Resume by downloading existing assets, never by trusting API digest alone.
        for asset in current['assets']:
            path = checked / asset['name']
            client.download(asset, path)
            if digest(path) != digest(files[asset['name']]):
                raise ValueError('Draft bytes differ; resume original run or choose a new rc tag')
        for name in sorted(files.keys() - set(names)):
            guarded()
            client.upload(release, files[name])
        current = guarded()
        names = [asset['name'] for asset in current['assets']]
        if len(names) != len(files) or set(names) != files.keys():
            raise ValueError('Uploaded asset set is incomplete or unexpected')
        for asset in current['assets']:
            path = checked / asset['name']
            client.download(asset, path)
            if digest(path) != digest(files[asset['name']]):
                raise ValueError('Downloaded asset differs from the verified build')
        verify_manifest(checked, version)
        subprocess.run(['sha256sum', '-c', 'SHA256SUMS.txt'], cwd=checked, check=True)
        guarded()
        # This is the sole publication mutation, after complete remote read-back.
        result = client.api(f'releases/{release["id"]}', 'PATCH',
                            dict(name=title, body=body, draft=False, prerelease=True, make_latest='false'))
        if result.get('draft') or not result.get('prerelease'):
            raise ValueError('Publication state is unconfirmed; inspect the release before retrying')
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare'])
    parser.add_argument('--artifacts', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    source, tag = os.environ['SOURCE_SHA'], os.environ['NEW_TAG']
    if not args.artifacts:
        parser.error('--artifacts is required')
    prepare_assets(args.artifacts, args.output, source, tag, os.environ['GITHUB_RUN_ID'], os.environ['GITHUB_SHA'])
    evidence = dict(schema=1, source_sha=source, tag=tag, run_id=os.environ['GITHUB_RUN_ID'],
                    workflow_sha=os.environ['GITHUB_SHA'], manifest_sha256=digest(args.output / 'SHA256SUMS.txt'),
                    reports=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(args.artifacts.rglob('verification.json'))])
    args.evidence.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('All five native targets passed; exact final filenames are covered by SHA256SUMS.txt. GUI review and promotion remain separate.')



if __name__ == '__main__':
    main()
