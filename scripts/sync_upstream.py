#!/usr/bin/env python3
"""Prepare a history-preserving upstream merge; the workflow builds before promotion."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess


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
    build_name = f"{version}-Codex-AI-zh-CN-auto.{upstream[:12]}"
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
        "  保留现有汉化，新增界面可能仍含英文；双平台验证以本次 Actions 结果为准，GUI 未人工验收。\n"
    )
    replace_once("README_zh-CN.md", r"## 未发布\n", notes)
    metadata.update(base_commit=upstream, version=version)
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
    # 本仓库的 CI 策略独立维护，也避免默认令牌推送上游 workflow 修改被拒绝。
    git("restore", "--source=HEAD", "--staged", "--worktree", "--", ".github/workflows")
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
