#!/usr/bin/env python3
"""Prepare immutable prerelease assets from the two verified platform packages."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil

from check_localization_release import ROOT, verify_release_notes
from release_notes import release_body, release_title, update_notes


def automatic_tag(metadata: dict) -> str:
    return f"{metadata['version']}-Codex-AI-zh-CN-auto.{metadata['base_commit'][:12]}"


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
    notes = release_body(tag, body, repository, args.source_sha, run_id, prerelease=True)
    Path("release-title.txt").write_text(release_title(tag, prerelease=True), encoding="utf-8")
    Path("release-notes.md").write_text(notes, encoding="utf-8")


if __name__ == "__main__":
    main()
