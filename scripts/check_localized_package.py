#!/usr/bin/env python3
"""Verify a release archive against source examples and required localized files."""
import argparse
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('archive', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
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
        if archive.read(prefix + name) != (root / name).read_bytes():
            raise SystemExit(f'Packaged document differs: {name}')
    examples = [p for p in (root / 'examples').rglob('*') if p.is_file()]
    for source in examples:
        name = prefix + 'Official_Examples/' + source.relative_to(root / 'examples').as_posix()
        if archive.read(name) != source.read_bytes():
            raise SystemExit(f'Packaged example differs: {name}')
    for source in (root / 'src/help/html').glob('*.html'):
        name = prefix + 'help/' + source.name
        if archive.read(name) != source.read_bytes():
            raise SystemExit(f'Packaged help differs: {name}')
    print(f'Archive verified: {args.archive.name}; {len(examples)} unchanged example files')
