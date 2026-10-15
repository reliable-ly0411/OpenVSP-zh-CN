#!/usr/bin/env python3
"""Names for published assets; source/tag identities and package bytes stay unchanged."""
import argparse
import hashlib
from pathlib import Path
from check_localization_release import TAG_RE

PLATFORMS = {'Ubuntu-24.04-x86_64': 'Ubuntu-24.04_amd64', 'Windows-x64': 'win64'}


def asset_name(tag, platform):
    match = TAG_RE.fullmatch(tag)
    if not match or platform not in PLATFORMS:
        raise ValueError('Invalid release tag or platform')
    return f"OpenVSP-{match.group('version')}-{PLATFORMS[platform]}-zh-CN.zip"


def asset_candidates(tag, platform):
    return (asset_name(tag, platform), f'OpenVSP-{tag}-{platform}.zip')


def selected_assets(directory, tag):
    names = {p.name for p in directory.iterdir() if p.is_file()}
    selected = {}
    for platform in PLATFORMS:
        matches = names.intersection(asset_candidates(tag, platform))
        if len(matches) != 1:
            raise ValueError('Missing or ambiguous platform asset')
        selected[platform] = directory / matches.pop()
    if names - {p.name for p in selected.values()} - {'SHA256SUMS.txt'}:
        raise ValueError('Unexpected release assets')
    return selected


def normalize(directory, tag):
    selected = selected_assets(directory, tag)  # Validate all names before any rename.
    for platform, path in selected.items():
        path.rename(directory / asset_name(tag, platform))


def verify_download(expected, downloaded, tag):
    wanted, actual = selected_assets(expected, tag), selected_assets(downloaded, tag)
    sums = {}
    for line in (downloaded / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.removeprefix('*').removeprefix('./')
        if name in sums or name not in {p.name for p in actual.values()}:
            raise ValueError('Unexpected or duplicate checksum entry')
        sums[name] = digest
    if set(sums) != {p.name for p in actual.values()}:
        raise ValueError('Missing checksum entry')
    for platform, path in actual.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != sums[path.name] or digest != hashlib.sha256(wanted[platform].read_bytes()).hexdigest():
            raise ValueError('Downloaded package checksum differs from verified build')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['normalize', 'verify'])
    parser.add_argument('--tag', required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--expected', type=Path)
    args = parser.parse_args()
    if args.command == 'normalize':
        normalize(args.directory, args.tag)
    elif args.expected is None:
        parser.error('--expected is required for verify')
    else:
        verify_download(args.expected, args.directory, args.tag)
