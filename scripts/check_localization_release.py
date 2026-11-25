#!/usr/bin/env python3
"""Fail closed when a localized OpenVSP tree is not ready to release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "src" / "cmake" / "VSP_Version.cmake"
RELEASE_NOTES_FILE = ROOT / "README_zh-CN.md"
TAG_RE = re.compile(
    r"^(?P<version>\d+\.\d+\.\d+)(?:-Codex-AI-zh-CN(?:-r[1-9]\d*|-auto\.(?P<upstream>[0-9a-f]{12}))?|-zh-CN\.rc\.[1-9]\d*|-zh-CN\.(?:dev|candidate)\.[0-9a-f]{12})$"
)


# Keep official upstream examples outside this supplemental directory unchanged.
AIRSHOW_356_MODELS = {
    'Community_Vans_RV-12.vsp3': '289590c6090a2e9b25578c4330b0aeaa1c5fd2a4e11de824caa1786b32f68e80',
    'NASA_N2A_Hybrid_Wing_Body.vsp3': '542d720d0131f0c46e8438c566ef878da5b4ce1091ea65bf3a6ac702e34ec2c3',
    'NASA_Six-Passenger_Tiltwing_UAM.vsp3': 'b50187604f1d170445a6abe8e97f8edb61b82514bccab23ce22ab88dd4719aa6',
    'NASA_X-57_Maxwell_Simplified_CRM_v4.4.1.vsp3': '4ff64f38baf3648806d99855b2f26519ad643f5fc6272617950921f78e8fe3b6',
    'Uber_eCRM-002_Lift-Plus-Cruise.vsp3': 'a5221c9ce64b3fdaaf4df6e9b7df96371be205ff2e640050b0a8fb95a16c421d',
}


def check_model_bytes(files):
    if set(files) != set(AIRSHOW_356_MODELS):
        raise ValueError("OpenVSP 3.56 must include only the five reviewed Airshow model files")
    for name, data in files.items():
        if hashlib.sha256(data).hexdigest() != AIRSHOW_356_MODELS[name]:
            raise ValueError("Airshow model bytes differ from reviewed source: " + name)


def check_source_models(path):
    check_model_bytes({model.name: model.read_bytes() for model in path.iterdir()
                       if model.suffix.lower() == ".vsp3"})


def check_archive_models(archive):
    files = {}
    for entry in archive.infolist():
        parts = PurePosixPath(entry.filename).parts
        if (len(parts) < 4 or parts[1:3] != ("Official_Examples", "Complete_Aircraft")
                or not parts[-1].lower().endswith(".vsp3")):
            continue
        if len(parts) != 4 or parts[-1] in files:
            raise ValueError("Additional or duplicate Airshow model entry: " + entry.filename)
        files[parts[-1]] = archive.read(entry)
    check_model_bytes(files)


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


def verify_bundled_model_data() -> tuple[int, int]:
    """Read the bundled models without translating or rewriting their names."""
    examples_dir = ROOT / "examples" / "Complete_Aircraft"
    models = sorted(examples_dir.glob("*.vsp3"))
    if not models:
        raise SystemExit("整机案例缺失：没有可校验的 .vsp3 模型")
    geometry_count = 0
    for model_path in models:
        try:
            root = ET.parse(model_path).getroot()
        except (ET.ParseError, OSError) as error:
            raise SystemExit(f"整机案例 XML 不可读：{model_path.name}: {error}") from error
        # Vehicle's direct Geom children own the model names. Nested Geom nodes
        # hold implementation details such as set membership and have no name.
        geoms = root.findall("./Vehicle/Geom")
        if not geoms:
            raise SystemExit(f"整机案例缺少几何体：{model_path.name}")
        for index, geom in enumerate(geoms, 1):
            name = geom.find("ParmContainer/Name")
            if name is None or len(name):
                raise SystemExit(f"整机案例缺少纯文本名称：{model_path.name}，几何体 {index}")
            # Empty names, whitespace, literal entities and UI-looking strings
            # are opaque model data. No dictionary lookup or normalization.
            geometry_count += 1
    return len(models), geometry_count


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
    global ROOT, VERSION_FILE, RELEASE_NOTES_FILE
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT, help="Source tree to inspect with trusted tooling")
    parser.add_argument("--expected-tag")
    parser.add_argument("--packaging-target", choices=("windows", "ubuntu-24.04-amd64"),
                        help="Explicit package target; omission keeps all original checks")
    parser.add_argument("--print-version", action="store_true")
    args = parser.parse_args()
    ROOT = args.source.resolve()
    VERSION_FILE = ROOT / "src" / "cmake" / "VSP_Version.cmake"
    RELEASE_NOTES_FILE = ROOT / "README_zh-CN.md"

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
        "vspIcon.ico",
        "vspIcon.png",
    ]
    windows_resource_required = args.packaging_target != "ubuntu-24.04-amd64"
    if windows_resource_required:
        required.append("src/vsp/vsp.rc.in")
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("本地化守卫失败，缺少文件：" + ", ".join(missing))

    require_text("README.md", f"本仓库基于 OpenVSP {version}，")
    require_text("README_zh-CN.md", f"当前软件版本：OpenVSP {version}\n")
    require_text("AGENTS.md", f"当前官方基线：OpenVSP {version}，")

    require_text("src/gui_and_draw/MainVSPScreen.cpp", "VSPVERSION4")
    require_text(
        "src/gui_and_draw/MainVSPScreen.cpp",
        "https://github.com/reliable-ly0411/OpenVSP-zh-CN",
    )
    require_text("src/gui_and_draw/VSPChinese.cpp", "VSPTranslate")
    if windows_resource_required:
        require_text("src/vsp/CMakeLists.txt", "vsp.rc.in")
    about = (ROOT / "src/gui_and_draw/MainVSPScreen.cpp").read_text(encoding="utf-8")
    if "【显著声明】" in about:
        raise SystemExit("本地化守卫失败：关于窗口仍包含旧的【显著声明】")

    if version == "3.56.0":
        try:
            check_source_models(ROOT / "examples" / "Complete_Aircraft")
        except (OSError, ValueError) as error:
            raise SystemExit(f"整机案例许可校验失败：{error}") from error

    bundled_model_count, bundled_geometry_count = verify_bundled_model_data()

    if args.expected_tag:
        match = TAG_RE.fullmatch(args.expected_tag)
        if not match:
            raise SystemExit(
                "新预发布标签必须为 <版本>-zh-CN.rc.<递增序号>；历史标签只用于校验，"
                f"例如 {version}-zh-CN.rc.1"
            )
        if match.group("version") != version:
            raise SystemExit(f"标签版本 {match.group('version')} 与源码版本 {version} 不一致")
        # 自动预发布标签固定到官方基线，避免错误版本对应到其他源码。
        if match.group("upstream") and match.group("upstream") != metadata["base_commit"][:12]:
            raise SystemExit("自动预发布标签与官方基线提交不一致")
        verify_release_notes(args.expected_tag)
        require_text("README_zh-CN.md", f"当前汉化版本：`{args.expected_tag}`")
        require_text("src/gui_and_draw/MainVSPScreen.cpp", f"汉化版本：{args.expected_tag}\\n")

    if args.print_version:
        print(version)
    else:
        print(
            f"本地化发布守卫通过：OpenVSP {version}，"
            f"整机案例 {bundled_model_count} 个，原始几何名称 {bundled_geometry_count} 项（只读校验）"
        )


if __name__ == "__main__":
    main()
