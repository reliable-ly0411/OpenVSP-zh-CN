#!/usr/bin/env python3
"""Fail closed when a localized OpenVSP tree is not ready to release."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "src" / "cmake" / "VSP_Version.cmake"
RELEASE_NOTES_FILE = ROOT / "README_zh-CN.md"
TAG_RE = re.compile(
    r"^(?P<version>\d+\.\d+\.\d+)-Codex-AI-zh-CN(?:-r[1-9]\d*)?$"
)


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


def verify_bundled_geometry_names() -> int:
    translation_source = (ROOT / "src" / "gui_and_draw" / "VSPChinese.cpp").read_text(
        encoding="utf-8"
    )
    translation_keys = set(
        re.findall(r'\{\s*"((?:\\.|[^"])*)"\s*,\s*"', translation_source)
    )

    geometry_names: set[str] = set()
    examples_dir = ROOT / "examples" / "Complete_Aircraft"
    for model_path in sorted(examples_dir.glob("*.vsp3")):
        root = ET.parse(model_path).getroot()
        for node in root.findall(".//Geom/ParmContainer/Name"):
            if node.text:
                geometry_names.add(node.text)

    missing_names = sorted(geometry_names - translation_keys)
    if missing_names:
        raise SystemExit(
            "整机案例几何体名称缺少显示翻译：" + ", ".join(missing_names)
        )
    return len(geometry_names)


def verify_release_notes(tag: str) -> None:
    text = RELEASE_NOTES_FILE.read_text(encoding="utf-8")
    section = re.search(
        rf"^## {re.escape(tag)}\s*$\n(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not section or not section.group("body").strip():
        raise SystemExit(
            f"发布更新说明缺失：请在 {RELEASE_NOTES_FILE.name} 添加“## {tag}”章节"
        )


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
        "AGENTS.md",
        "README.md",
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
    require_text("src/gui_and_draw/MainVSPScreen.cpp", "VSPVERSION4")
    require_text(
        "src/gui_and_draw/MainVSPScreen.cpp",
        "https://github.com/reliable-ly0411/OpenVSP-zh-CN",
    )
    require_text("src/gui_and_draw/VSPChinese.cpp", "VSPTranslate")
    require_text("src/vsp/CMakeLists.txt", "vsp.rc.in")
    about = (ROOT / "src/gui_and_draw/MainVSPScreen.cpp").read_text(encoding="utf-8")
    if "【显著声明】" in about:
        raise SystemExit("本地化守卫失败：关于窗口仍包含旧的【显著声明】")

    bundled_geometry_name_count = verify_bundled_geometry_names()

    if args.expected_tag:
        match = TAG_RE.fullmatch(args.expected_tag)
        if not match:
            raise SystemExit(
                "发布标签必须为 <版本>-Codex-AI-zh-CN 或其 -rN 重发版本，"
                "例如 3.52.0-Codex-AI-zh-CN-r2"
            )
        if match.group("version") != version:
            raise SystemExit(f"标签版本 {match.group('version')} 与源码版本 {version} 不一致")
        verify_release_notes(args.expected_tag)

    if args.print_version:
        print(version)
    else:
        print(
            f"本地化发布守卫通过：OpenVSP {version}，"
            f"整机案例几何体名称 {bundled_geometry_name_count} 项"
        )


if __name__ == "__main__":
    main()
