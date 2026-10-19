#!/usr/bin/env python3
"""An explicit, immutable source/new-tag contract for all five native targets."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from backfill_plan import RELEASES

TAG_RE = re.compile(r'^(?P<version>\d+\.\d+\.\d+)-zh-CN\.rc\.(?P<revision>[1-9]\d*)$')
PLATFORMS = (
    dict(platform='Ubuntu-24.04_amd64', runner='ubuntu-24.04', arch='x86_64', python='3.12', llvm=''),
    dict(platform='Ubuntu-24.04_arm64-Python3.12', runner='ubuntu-24.04-arm', arch='aarch64', python='3.12', llvm=''),
    dict(platform='win64', runner='windows-2022', arch='x86_64', python='3.11', llvm=''),
    dict(platform='macOS-14-arm64-Python3.11', runner='macos-14', arch='arm64', python='3.11', llvm='16'),
    dict(platform='macOS-15-x86_64-Python3.11', runner='macos-15-intel', arch='x86_64', python='3.11', llvm='16'),
)
REQUIRED_CHECKS = {
    'native architecture', 'dependency closure / RPATH', 'Chinese CLI help',
    'AngelScript model smoke', 'model-name roundtrip', 'Unicode filename and persisted names',
    'custom geometry from empty cwd',
    'Python extension import/version', 'fresh requirements install/import',
    'source examples/help/documents byte equality', 'ZIP integrity', 'privacy scan',
    'unchanged tracked source',
}


def validate_inputs(source_sha, new_tag):
    if not re.fullmatch('[0-9a-f]{40}', source_sha):
        raise ValueError('source_sha must be an exact lowercase 40-character commit')
    match = TAG_RE.fullmatch(new_tag)
    if not match or match['version'] not in {v for v, _, _ in RELEASES}:
        raise ValueError('new_tag must be a supported <version>-zh-CN.rc.<positive integer>')
    return match['version']


def asset_name(version, platform):
    if version not in {v for v, _, _ in RELEASES} or platform not in {p['platform'] for p in PLATFORMS}:
        raise ValueError('Unsupported version family or native platform')
    return f'OpenVSP-{version}-{platform}-zh-CN.zip'


def matrix(source_sha, new_tag):
    version = validate_inputs(source_sha, new_tag)
    return {'include': [dict(version=version, tag=new_tag, sha=source_sha, **p) for p in PLATFORMS]}


def validate_source(source, source_sha, new_tag):
    version = validate_inputs(source_sha, new_tag)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(source), *args], text=True).strip()
    if git('rev-parse', 'HEAD') != source_sha:
        raise ValueError('Checked-out source does not match source_sha')
    baseline = next(sha for v, _, sha in RELEASES if v == version)
    subprocess.run(['git', '-C', str(source), 'merge-base', '--is-ancestor', baseline, source_sha], check=True)
    text = (source / 'src/cmake/VSP_Version.cmake').read_text(encoding='utf-8')
    actual = '.'.join(re.search(rf'SET\(\s*VSPVER_{key}\s+(\d+)\s*\)', text)[1]
                      for key in ('MAJOR', 'MINOR', 'PATCH'))
    if actual != version:
        raise ValueError('Tag version does not match source version')
    if git('status', '--porcelain', '--untracked-files=no'):
        raise ValueError('Tracked source files changed')
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    source_sha, tag = os.environ['SOURCE_SHA'], os.environ['NEW_TAG']
    version = validate_source(args.source, source_sha, tag)
    result = matrix(source_sha, tag)
    if output := os.environ.get('GITHUB_OUTPUT'):
        with open(output, 'a', encoding='utf-8') as f:
            f.write('matrix=' + json.dumps(result, separators=(',', ':')) + '\n')
            f.write('version=' + version + '\n')
    print(f'Validated {tag}: five native targets from {source_sha}; historical releases are untouched')


if __name__ == '__main__':
    main()
