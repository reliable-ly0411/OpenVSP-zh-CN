#!/usr/bin/env python3
"""Render one consistent title and six-section body for localized releases."""
import argparse
import os
from pathlib import Path
import re

from check_localization_release import ROOT, TAG_RE


def update_notes(readme: str, tag: str) -> str:
    section = re.search(rf"^## {re.escape(tag)}\s*$\n(.*?)(?=^## |\Z)", readme, re.MULTILINE | re.DOTALL)
    if not section or not section.group(1).strip():
        raise ValueError(f"缺少标签 {tag} 对应的更新说明")
    return section.group(1).strip()


def release_title(tag: str, prerelease: bool = False) -> str:
    match = TAG_RE.fullmatch(tag)
    if not match:
        raise ValueError(f"无效汉化标签：{tag}")
    suffix = []
    if match.group('upstream'):
        suffix = ['自动预发布', match.group('upstream')]
    else:
        revision = re.search(r'-r[1-9]\d*$', tag)
        if revision:
            suffix.append(revision.group()[1:])
        if prerelease:
            suffix.append('预发布')
    return f"OpenVSP {match.group('version')} Codex AI 简体中文版" + (f"（{' · '.join(suffix)}）" if suffix else '')


def release_body(tag: str, changes: str, repository: str, source_sha: str, run_id: str,
                 prerelease: bool = False) -> str:
    # Validate before building filenames or links.
    release_title(tag, prerelease)
    version = TAG_RE.fullmatch(tag).group('version')
    automatic = '-auto.' in tag
    status = '自动预发布' if automatic else '预发布' if prerelease else '正式发布'
    base = f'https://github.com/{repository}/releases/download/{tag}'
    rows = []
    for label, platform in [('Ubuntu 24.04 x86_64', 'Ubuntu-24.04-x86_64'), ('Windows x64', 'Windows-x64')]:
        filename = f'OpenVSP-{tag}-{platform}.zip'
        rows.append(f'| {label} | [{filename}]({base}/{filename}) |')
    rows.append(f'| SHA-256 清单 | [SHA256SUMS.txt]({base}/SHA256SUMS.txt) |')
    downloads = '\n'.join(rows)
    gui = ('新增界面可能仍含英文；Linux/Windows GUI 未人工验收。' if automatic else
           'GUI 抽查范围以本次更新及发布页后续记录为准；自动构建成功不代表 GUI 全面验收。')
    return f'''## 版本信息

- OpenVSP：`{version}`
- 发布标签：`{tag}`
- 发布类型：{status}
- 二进制平台：Windows x64、Ubuntu 24.04 x86_64
- 源码提交：`{source_sha}`

## 本次更新

{changes.strip()}

## 下载与校验

| 内容 | 下载 |
| --- | --- |
{downloads}

下载后按 `SHA256SUMS.txt` 核对：Linux 使用 `sha256sum 文件名.zip`，Windows PowerShell 使用 `Get-FileHash 文件名.zip -Algorithm SHA256`。
解压后运行 Linux 的 `vsp` 或 Windows 的 `vsp.exe`。页面底部的 Source code ZIP / tar.gz 对应本标签源码。

## 验证情况

GitHub 托管的 Ubuntu 24.04 与 Windows 2022 x64 双平台构建、中文命令行、翻译回归、模型保存重开与机身转换冒烟、压缩包内容检查通过。
资产公开前下载复核 SHA-256；[完整构建与校验记录](https://github.com/{repository}/actions/runs/{run_id})。
{gui}

## 兼容性与限制

- Linux 显示中文需安装 `fonts-noto-cjk`。
- 文件格式、API、内部参数 ID、用户名称及克隆名称后缀保持原样，仅翻译显示文本。
- 未据此验收全部 GUI、VSPAERO/CFD/FEA 求解、FitModel 优化、数值收敛或 GPU 性能。

## 许可与归属

这是由 OpenAI Codex AI 生成并维护的非官方简体中文本地化构建。OpenVSP 原软件版权、作者归属及 NOSA 1.3 许可不变；[官方上游](https://github.com/OpenVSP/OpenVSP)。
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--source-sha', required=True)
    parser.add_argument('--prerelease', action='store_true')
    args = parser.parse_args()
    changes = update_notes((ROOT / 'README_zh-CN.md').read_text(encoding='utf-8'), args.tag)
    Path('release-title.txt').write_text(release_title(args.tag, args.prerelease), encoding='utf-8')
    Path('release-notes.md').write_text(release_body(args.tag, changes, os.environ['GITHUB_REPOSITORY'],
                                                  args.source_sha, os.environ['GITHUB_RUN_ID'], args.prerelease), encoding='utf-8')


if __name__ == '__main__':
    main()
