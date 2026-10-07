#!/usr/bin/env python3
"""Verify a release archive against source examples and required localized files."""
import argparse
from pathlib import Path
import subprocess
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('archive', type=Path)
parser.add_argument('--windows-checkout', action='store_true',
                    help='按 Git 属性生成 Windows 检出字节，供 Linux 发布任务复核 Windows 包')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]


def source_bytes(source: Path) -> bytes:
    if not args.windows_checkout:
        return source.read_bytes()
    # 交给 Git 应用 text/eol 属性；不能统一替换换行，否则会漏检模型或二进制损坏。
    path = source.relative_to(root).as_posix()
    return subprocess.run(
        ['git', '-C', str(root), '-c', 'core.autocrlf=true', '-c', 'core.eol=crlf',
         'cat-file', '--filters', 'HEAD:' + path],
        check=True, capture_output=True,
    ).stdout


with zipfile.ZipFile(args.archive) as archive:
    bad = archive.testzip()
    if bad:
        raise SystemExit(f'Corrupt archive entry: {bad}')
    names = archive.namelist()
    roots = {n.split('/')[0] for n in names if '/' in n}
    if len(roots) != 1:
        raise SystemExit('Expected one package root')
    prefix = roots.pop() + '/'
    suffix = '.exe' if prefix + 'vsp.exe' in names else ''
    for executable in ('vsp', 'vspscript', 'vspaero', 'vspviewer', 'vsploads'):
        if prefix + executable + suffix not in names:
            raise SystemExit(f'Missing executable: {executable}{suffix}')
    for resource in ('help/vsp_help', 'help/github-pandoc.css'):
        if prefix + resource not in names:
            raise SystemExit(f'Missing resource: {resource}')
    for name in ('README.md', 'README_zh-CN.md', 'AGENTS.md', 'LICENSE', 'vspIcon.png'):
        if archive.read(prefix + name) != source_bytes(root / name):
            raise SystemExit(f'Packaged document differs: {name}')
    examples = [p for p in (root / 'examples').rglob('*') if p.is_file()]
    for source in examples:
        name = prefix + 'Official_Examples/' + source.relative_to(root / 'examples').as_posix()
        if archive.read(name) != source_bytes(source):
            raise SystemExit(f'Packaged example differs: {name}')
    for source in (root / 'src/help/html').glob('*.html'):
        name = prefix + 'help/' + source.name
        if archive.read(name) != source_bytes(source):
            raise SystemExit(f'Packaged help differs: {name}')
    print(f'Archive verified: {args.archive.name}; {len(examples)} unchanged example files')
