#!/usr/bin/env python3
"""Fail closed when a localized OpenVSP tree is not ready to release."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "src" / "cmake" / "VSP_Version.cmake"
TAG_RE = re.compile(r"^(?P<version>\d+\.\d+\.\d+)-Codex-AI-zh-CN$")


def read_version() -> str:
    text = VERSION_FILE.read_text(encoding="utf-8")
    values = {}
    for key in ("MAJOR", "MINOR", "PATCH"):
        match = re.search(rf"SET\(\s*VSPVER_{key}\s+(\d+)\s*\)", text)
        if not match:
            raise SystemExit(f"无法从 {VERSION_FILE} 读取 VSPVER_{key}")
        values[key] = match.group(1)
    return f"{values['MAJOR']}.{values['MINOR']}.{values['PATCH']}"


def require_text(path: str, needle: str) -> None:
    content = (ROOT / path).read_text(encoding="utf-8")
    if needle not in content:
        raise SystemExit(f"本地化守卫失败：{path} 缺少 {needle!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-tag")
    parser.add_argument("--print-version", action="store_true")
    args = parser.parse_args()

    version = read_version()
    metadata = json.loads((ROOT / ".github" / "upstream.json").read_text(encoding="utf-8"))
    if metadata.get("version") != version:
        raise SystemExit(
            f"上游基线版本 {metadata.get('version')!r} 与源码版本 {version!r} 不一致"
        )

    required = [
        "AI_LOCALIZATION_HANDOFF.md",
        "README_zh-CN.md",
        "src/gui_and_draw/VSPChinese.cpp",
        "src/gui_and_draw/VSPChinese.h",
        "src/vsp/vsp.rc.in",
        "vspIcon.ico",
        "vspIcon.png",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("本地化守卫失败，缺少文件：" + ", ".join(missing))

    require_text("src/gui_and_draw/MainVSPScreen.cpp", "【声明】本中文本地化")
    require_text("src/gui_and_draw/VSPChinese.cpp", "VSPTranslate")
    require_text("src/vsp/CMakeLists.txt", "vsp.rc.in")
    about = (ROOT / "src/gui_and_draw/MainVSPScreen.cpp").read_text(encoding="utf-8")
    if "【显著声明】" in about:
        raise SystemExit("本地化守卫失败：关于窗口仍包含旧的【显著声明】")

    if args.expected_tag:
        match = TAG_RE.fullmatch(args.expected_tag)
        if not match:
            raise SystemExit(
                "发布标签必须为 <版本>-Codex-AI-zh-CN，例如 3.52.0-Codex-AI-zh-CN"
            )
        if match.group("version") != version:
            raise SystemExit(f"标签版本 {match.group('version')} 与源码版本 {version} 不一致")

    if args.print_version:
        print(version)
    else:
        print(f"本地化发布守卫通过：OpenVSP {version}")


if __name__ == "__main__":
    main()
