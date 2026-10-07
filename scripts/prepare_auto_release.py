#!/usr/bin/env python3
"""Prepare immutable prerelease assets from the two verified platform packages."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

from check_localization_release import ROOT, verify_release_notes


def automatic_tag(metadata: dict) -> str:
    return f"{metadata['version']}-Codex-AI-zh-CN-auto.{metadata['base_commit'][:12]}"


def update_notes(readme: str, tag: str) -> str:
    section = re.search(
        rf"^## {re.escape(tag)}\s*$\n(.*?)(?=^## |\Z)",
        readme, re.MULTILINE | re.DOTALL,
    )
    if not section or not section.group(1).strip():
        raise ValueError(f"缺少标签 {tag} 对应的更新说明")
    return section.group(1).strip()


def prepare_assets(packages: Path, output: Path, source_sha: str, tag: str) -> None:
    # 仅接受该提交的两个已验证 ZIP，避免把别次运行或缺少平台的产物公开。
    platforms = ("Ubuntu-24.04-x86_64", "Windows-x64")
    expected = {f"OpenVSP-{source_sha}-{platform}.zip" for platform in platforms}
    if {path.name for path in packages.glob("*.zip")} != expected:
        raise ValueError("必须提供同一源码提交的 Linux 与 Windows 构建包")
    output.mkdir()
    checksums = []
    for platform in platforms:
        target = output / f"OpenVSP-{tag}-{platform}.zip"
        shutil.copyfile(packages / f"OpenVSP-{source_sha}-{platform}.zip", target)
        # ZIP 保持原始字节，只调整外部下载文件名；SHA-256 针对实际发布资产。
        with target.open("rb") as handle:
            checksum = hashlib.file_digest(handle, "sha256").hexdigest()
        checksums.append(f"{checksum}  {target.name}\n")
    (output / "SHA256SUMS.txt").write_text("".join(checksums), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-tag", action="store_true")
    parser.add_argument("--source-sha")
    parser.add_argument("--packages", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    metadata = json.loads((ROOT / ".github/upstream.json").read_text(encoding="utf-8"))
    tag = automatic_tag(metadata)
    if args.print_tag:
        print(tag)
        return
    if not all((args.source_sha, args.packages, args.output)):
        parser.error("准备资产需要 --source-sha、--packages 和 --output")
    verify_release_notes(tag)
    body = update_notes((ROOT / "README_zh-CN.md").read_text(encoding="utf-8"), tag)
    prepare_assets(args.packages, args.output, args.source_sha, tag)
    repository = os.environ["GITHUB_REPOSITORY"]
    run_id = os.environ["GITHUB_RUN_ID"]
    notes = (
        f"OpenVSP {metadata['version']} 简体中文自动构建（预发布）。\n\n"
        "Linux/Windows 编译、中文命令行、翻译回归、模型冒烟和打包检查通过。\n"
        "**新增界面可能仍含英文；Linux/Windows GUI 未人工验收。**\n\n"
        f"## 本次更新\n\n{body}\n\n"
        f"- 源码提交：`{args.source_sha}`\n"
        f"- 官方基线：`{metadata['base_commit']}`\n"
        f"- [完整构建与校验记录](https://github.com/{repository}/actions/runs/{run_id})\n\n"
        "附件包含两平台 ZIP 和 SHA-256 清单，页面源码归档对应本标签。\n"
        "本地化由 OpenAI Codex AI 生成并维护；原作者归属及 NOSA 1.3 许可不变。\n"
    )
    Path("release-notes.md").write_text(notes, encoding="utf-8")


if __name__ == "__main__":
    main()
