#!/usr/bin/env python3
"""Prepare a history-preserving isolated upstream candidate; no automatic promotion."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess


# Only downstream maintenance policy is retained; product scripts merge normally.
TRUSTED_POLICY_PATHS = (
    ".github/workflows", "AGENTS.md",
    "scripts/sync_upstream.py", "scripts/select_official_release.py",
    "scripts/check_localization_release.py",
)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], text=True, capture_output=True, check=check)


def replace_once(path: str, pattern: str, replacement: str) -> None:
    target = Path(path)
    text, count = re.subn(pattern, lambda _: replacement, target.read_text(encoding="utf-8"))
    if count != 1:
        raise RuntimeError(f"{path} 的当前版本字段匹配 {count} 次，需要人工检查")
    target.write_text(text, encoding="utf-8")


def update_metadata(metadata: dict, upstream: str) -> str:
    version_text = Path("src/cmake/VSP_Version.cmake").read_text(encoding="utf-8")
    version = ".".join(
        re.search(rf"SET\(\s*VSPVER_{key}\s+(\d+)\s*\)", version_text).group(1)
        for key in ("MAJOR", "MINOR", "PATCH")
    )
    # 自动构建单独标识，不能冒充已验收的不可变 Release 标签。
    source_ref = os.environ.get("UPSTREAM_SOURCE_REF", "")
    release_tag = re.fullmatch(r"(?:refs/tags/)?OpenVSP_(\d+\.\d+\.\d+)", source_ref)
    if release_tag and release_tag[1] != version:
        raise ValueError("Official tag name and source software version disagree")
    kind = "candidate" if release_tag else "dev"
    build_name = f"{version}-zh-CN.{kind}.{upstream[:12]}"
    replace_once("README.md", r"本仓库基于 OpenVSP \d+\.\d+\.\d+，", f"本仓库基于 OpenVSP {version}，")
    replace_once("README_zh-CN.md", r"当前软件版本：OpenVSP \d+\.\d+\.\d+\n", f"当前软件版本：OpenVSP {version}\n")
    replace_once("README_zh-CN.md", r"当前汉化版本：`[^`]+`", f"当前汉化版本：`{build_name}`")
    replace_once(
        "AGENTS.md",
        r"当前官方基线：OpenVSP \d+\.\d+\.\d+，提交\s*`[0-9a-f]{40}`",
        f"当前官方基线：OpenVSP {version}，提交\n  `{upstream}`",
    )
    replace_once(
        "src/gui_and_draw/MainVSPScreen.cpp",
        r"汉化版本：[^\"\n]+\\n",
        f"汉化版本：{build_name}\\n",
    )
    previous = metadata["base_commit"]
    notes = (
        f"## 未发布\n\n## {build_name}\n\n- 自动同步官方 OpenVSP {version}：`{previous[:12]}` → `{upstream[:12]}`。\n"
        f"  [上游变更](https://github.com/{metadata['repository']}/compare/{previous}...{upstream})；\n"
        f"  上游来源：{source_ref or '未标记开发提交'}；{'官方发布标签候选' if release_tag else '开发快照，非官方已发布版本'}。\n"
        "  保留现有汉化，新增界面可能仍含英文；仅构建候选产物，GUI 未人工验收，不自动公开 Release。\n"
    )
    replace_once("README_zh-CN.md", r"## 未发布\n", notes)
    metadata.update(base_commit=upstream, version=version, source_ref=source_ref,
                    source_kind="official-release" if release_tag else "development-snapshot")
    Path(".github/upstream.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    git("add", "--", ".github/upstream.json", "README.md", "README_zh-CN.md", "AGENTS.md", "src/gui_and_draw/MainVSPScreen.cpp")
    return version


def prepare(upstream_ref: str) -> dict:
    metadata = json.loads(Path(".github/upstream.json").read_text(encoding="utf-8"))
    localized = git("rev-parse", "HEAD").stdout.strip()
    upstream = git("rev-parse", "--verify", f"{upstream_ref}^{{commit}}").stdout.strip()
    if git("merge-base", "--is-ancestor", upstream, localized, check=False).returncode == 0:
        return {"changed": "false", "sha": localized, "upstream_sha": upstream}
    # 上游重写历史或基线损坏时停止，不能把无关历史当作正常升级。
    for tip in (localized, upstream):
        git("merge-base", "--is-ancestor", metadata["base_commit"], tip)

    merged = git("merge", "--no-ff", "--no-commit", upstream, check=False)
    print(merged.stdout + merged.stderr, end="")
    if merged.returncode not in (0, 1):
        raise RuntimeError("Git 合并失败")
    # Retain only the explicit trusted maintenance policy, not all scripts/.
    # The running sync/guard tools are copied from main before this merge.
    for path in TRUSTED_POLICY_PATHS:
        if git("cat-file", "-e", f"HEAD:{path}", check=False).returncode == 0:
            git("restore", "--source=HEAD", "--staged", "--worktree", "--", path)
    conflicts = git("diff", "--name-only", "--diff-filter=U").stdout.strip()
    if conflicts:
        raise RuntimeError(f"上游同步存在代码冲突，未创建提交或更新主分支：\n{conflicts}")

    version = update_metadata(metadata, upstream)
    return {"changed": "true", "version": version, "upstream_sha": upstream}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    # 可换成已获取的官方标签或提交，例如 refs/remotes/official/main；不接受仓库 URL。
    parser.add_argument("upstream_ref", nargs="?", default="FETCH_HEAD")
    args = parser.parse_args()
    result = prepare(args.upstream_ref)
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a", encoding="utf-8") as handle:
            for key, value in result.items():
                handle.write(f"{key}={value}\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
