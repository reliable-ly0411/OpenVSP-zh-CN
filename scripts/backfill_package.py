#!/usr/bin/env python3
"""Check a native ZIP against Git bytes at the historical source checkout."""
from pathlib import Path, PurePosixPath
import subprocess
import sys
import zipfile


def verify(archive_path, source):
    tracked = subprocess.check_output(['git', '-C', str(source), 'ls-files', '-z']).decode().split('\0')
    expected = {}
    for name in ('README.md', 'README_zh-CN.md', 'AGENTS.md', 'LICENSE', 'CHANGELOG.md', 'vspIcon.png'):
        expected[name] = name
    for name in ('AI_LOCALIZATION_HANDOFF.md', 'LOCALIZATION_CHANGELOG.md'):
        if name in tracked:
            expected[name] = name
    for name in tracked:
        if name.startswith('examples/'):
            expected['Official_Examples/' + name.removeprefix('examples/')] = name
        if name.startswith('src/help/images/'):
            expected[name.removeprefix('src/')] = name
        if name.startswith('src/help/html/') and name.endswith('.html'):
            expected['help/' + Path(name).name] = name
    expected.update({'help/vsp_help': 'src/help/vsp_help',
                     'help/github-pandoc.css': 'src/help/github-pandoc.css'})
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive entries')
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name:
                raise ValueError('Unsafe archive entry')
        roots = {n.split('/')[0] for n in names}
        if len(roots) != 1:
            raise ValueError('Expected one package root')
        prefix = roots.pop() + '/'
        for program in ('vsp', 'vspscript', 'vspaero', 'vspviewer', 'vsploads'):
            if prefix + program not in names:
                raise ValueError(f'Missing executable: {program}')
        for destination, original in expected.items():
            data = subprocess.check_output(['git', '-C', str(source), 'show', 'HEAD:' + original])
            if archive.read(prefix + destination) != data:
                raise ValueError(f'Package differs from immutable source: {destination}')
        if archive.testzip():
            raise ValueError('Invalid ZIP CRC')
    return len(expected)

if __name__ == '__main__':
    count = verify(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f'Immutable source files verified: {count}')
