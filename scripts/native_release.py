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
from native_functional import validate_functional_summary
from native_plan import PLATFORMS, REQUIRED_CHECKS, asset_name, validate_inputs
from upstream_release_notes import upstream_release_notes


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
    validate_functional_summary(report.get('functional_smoke'))
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
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Invalid repository')
    upstream, original = upstream_release_notes(version)
    revision = int(tag.rsplit('.', 1)[1])
    source_url = f'https://github.com/{repository}/blob/{source_sha}'
    changes = [
        '界面显示本地化、模型名称持久化边界、中文帮助和运行资源布局修复。',
        '固定 Python/NumPy ABI；Windows 中文 STL 导出和 VSPAERO 路径扫描修复。',
    ]
    if revision >= 2:
        changes += [
            'rc.2 新增：文件选择器标题补译并纳入静态入口扫描；参数窗口和属性对象标题保留用户原名、描述及路径。',
            'rc.2 新增：工程术语按实际上下文审校，保留技术标识和不确定的准确英文；补齐随包来源说明、文档及链接验证。',
        ]
        if version in ('3.54.0', '3.55.0'):
            changes.append('rc.2 新增：接通分割与缝合导出失败提示的显示翻译，错误详情和文件路径保持原样。')
    gui = ('五个平台均经原生构建和包内 CLI、模型读写、分析、Python 导入、依赖与校验检查。'
           'Linux AMD64 原始 ZIP 的主界面、机翼页及模型名称/路径回归已人工抽查；'
           'Windows、macOS 和 Linux ARM64 GUI 未作同范围人工验收。'
           if linux_gui_reviewed else
           '原生构建和 GUI 截图待目视及原包复核；此准备文本本身不代表发布验收通过。')
    family_note = ('3.51.2 源码保留早期独立导入历史；对应官方版本的 CHANGELOG 字节一致，'
                   '尚未接续该官方标签的 Git 祖先。\n\n' if version == '3.51.2' else '')
    mac_difference = ('官方此版本 ARM64 下载名使用 macOS 15；本仓按实际 macOS 14 原生目标命名，'
                      '不把二者视为相同二进制。' if version in ('3.54.0', '3.55.0') else
                      'macOS 下载名沿用对应官方版本的平台拼写。')
    rows = '\n'.join(f'| {p["platform"]} | `{asset_name(version, p["platform"])}` |' for p in PLATFORMS)
    return (
        f'OpenVSP {version} 非官方简体中文预发布，汉化修订 `{tag}`。'
        'OpenVSP 原软件版权、作者归属及 NOSA 1.3 许可不变。\n\n'
        f'源码：[`{source_sha}`]({source_url})；官方版本参考：'
        f'[`{upstream["upstream_tag"]}`](https://github.com/OpenVSP/OpenVSP/commit/{upstream["upstream_sha"]})。\n\n'
        + family_note + '## 本地变化\n\n' + ''.join('- ' + change + '\n' for change in changes)
        + '\n## 下载与校验\n\n| 实际目标 | 文件名 |\n|---|---|\n' + rows + '\n\n'
        '附件仅五个 ZIP 和 `SHA256SUMS.txt`。同一软件版本的不同 rc 可能使用相同 ZIP 基名，'
        '请按标签分目录保存，只与同一 Release 的清单配对。下载全部五包可运行 '
        '`sha256sum -c SHA256SUMS.txt`；只下载一包时计算该文件 SHA-256 并与清单同名行逐字核对。'
        'macOS 可用 `shasum -a 256`，Windows 可用 `Get-FileHash -Algorithm SHA256`。\n\n'
        '对照[官方旧版下载页](https://openvsp.org/download_old.php)：Windows 与 Intel Mac 沿用上游文件名结构并加 `-zh-CN`；'
        '官方 Ubuntu AMD64 为 `.deb`，本仓提供便携 ZIP；Ubuntu ARM64 是本仓新增目标。'
        + mac_difference + '\n\n'
        '## 安装、兼容性与限制\n\n'
        '- 校验后完整解压，保留运行资源目录。Linux 需要中文字体；3.51.x 使用随包 `vsp-zh-CN` 启动器。\n'
        '- Linux Python 3.12，Windows/macOS Python 3.11；NumPy 1.26.4，依赖约束 `<2`。使用 Python API 前按随包 requirements 配置独立环境。\n'
        '- macOS 使用本地 ad-hoc 签名，尚未公证。平台名描述实际构建目标，不额外宣称未测试的旧系统兼容性。\n'
        '- 八个整机示例全部保留。其中三个社区模型的来源标注为 CC BY-SA，具体许可版本尚未查明；再分发或商用前须另行核对，不能据本说明推断已补齐授权。\n\n'
        '## 验证范围\n\n' + gui + '\n\n'
        f'[使用说明与技术验证]({source_url}/README_zh-CN.md)。'
        + (f'[第三方内容与社区模型来源]({source_url}/THIRD_PARTY_NOTICES.md)。' if revision >= 2 else
           f'[社区模型来源记录]({source_url}/examples/Complete_Aircraft/SOURCES_AND_LICENSES.md)。')
        + '\n\n## 上游版本说明（全文）\n\n'
        '官方仓库在本次核查时没有 GitHub Release 条目；以下完整保留对应官方标签 `CHANGELOG.md` 的版本章节。'
        '其中作者口吻、工具及 AI 开发叙述均为上游作者原文，不是本地化维护者的成果声明。'
        '原文中指向不存在 GitHub Release 的历史链接也原样保留，请使用下列官网公告和固定源码链接核对。\n\n'
        f'[官网公告]({upstream["announcement_url"]}) · '
        f'[完整原始 CHANGELOG 与精确提交]({upstream["source_url"]}) · '
        f'[上游 NOSA 1.3 许可]({upstream["license_url"]})\n\n'
        '<details>\n<summary>展开上游作者原文</summary>\n\n' + original + '\n</details>\n'
    )


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
