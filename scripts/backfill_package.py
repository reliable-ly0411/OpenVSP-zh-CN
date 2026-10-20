#!/usr/bin/env python3
"""Check a native ZIP against Git bytes at the historical source checkout."""
from pathlib import Path, PurePosixPath
import subprocess
import sys
import zipfile


def verify(archive_path, source, runtime_resources=False):
    tracked = subprocess.check_output(['git', '-C', str(source), 'ls-files', '-z']).decode().split('\0')
    expected = {}
    for name in ('README.md', 'README_zh-CN.md', 'AGENTS.md', 'LICENSE', 'CHANGELOG.md', 'vspIcon.png'):
        expected[name] = name
    for name in ('AI_LOCALIZATION_HANDOFF.md', 'LOCALIZATION_CHANGELOG.md'):
        if name in tracked:
            expected[name] = name
    # Old immutable source tags did not promise the evidence document tree.
    # New notices opt the corresponding source revision into the complete docs
    # requirement; do not retroactively reject or alter historical packages.
    if 'THIRD_PARTY_NOTICES.md' in tracked:
        expected['THIRD_PARTY_NOTICES.md'] = 'THIRD_PARTY_NOTICES.md'
        expected.update({name: name for name in tracked if name.startswith('docs/')})
    for name in tracked:
        if name.startswith('examples/'):
            expected['Official_Examples/' + name.removeprefix('examples/')] = name
            relative = name.removeprefix('examples/')
            if runtime_resources and relative.split('/')[0] in ('airfoil', 'CustomScripts', 'scripts', 'textures', 'vspaero_ex', 'CCE', 'matlab'):
                expected[relative] = name
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
        windows = prefix + 'vsp.exe' in names
        for program in ('vsp', 'vspscript', 'vspaero', 'vspviewer', 'vsploads'):
            if prefix + program + ('.exe' if windows else '') not in names:
                raise ValueError(f'Missing executable: {program}')
        for destination, original in expected.items():
            command = ['git', '-C', str(source)]
            command += (['-c', 'core.autocrlf=true', '-c', 'core.eol=crlf', 'cat-file', '--filters', 'HEAD:' + original]
                        if windows else ['show', 'HEAD:' + original])
            data = subprocess.check_output(command)
            if archive.read(prefix + destination) != data:
                raise ValueError(f'Package differs from immutable source: {destination}')
        if archive.testzip():
            raise ValueError('Invalid ZIP CRC')
    return len(expected)

if __name__ == '__main__':
    count = verify(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f'Immutable source files verified: {count}')
