#!/usr/bin/env python3
"""Select an official release tag, never label untagged main as a release."""
import os
import re
import subprocess


def select_ref(remote_tags, override=''):
    if override:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./-]*', override) or '..' in override:
            raise ValueError('Invalid explicit official ref')
        return override
    tags = {}
    for line in remote_tags.splitlines():
        match = re.fullmatch(r'[0-9a-f]{40}\s+refs/tags/(OpenVSP_(\d+)\.(\d+)\.(\d+))(?:\^\{\})?', line)
        if match:
            tags[tuple(map(int, match.groups()[1:]))] = match[1]
    if not tags:
        raise ValueError('No official version tags found; refusing to silently follow main')
    return tags[max(tags)]


def main():
    override = os.environ.get('UPSTREAM_REF', '').strip()
    remote_tags = '' if override else subprocess.check_output([
        'git', 'ls-remote', '--tags', 'https://github.com/OpenVSP/OpenVSP.git', 'refs/tags/OpenVSP_*'], text=True)
    print(select_ref(remote_tags, override))


if __name__ == '__main__':
    main()
