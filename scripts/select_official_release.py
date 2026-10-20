#!/usr/bin/env python3
"""Select a source ref, not publication evidence; daily sync follows main."""
import os
import re


def select_ref(remote_tags='', override=''):
    # Retain the argument for callers of this historical filename. Version tags
    # cannot establish publication, and must never select an automatic build.
    if override:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./-]*', override) or '..' in override:
            raise ValueError('Invalid explicit official ref')
        return override
    return 'main'


def main():
    override = os.environ.get('UPSTREAM_REF', '').strip()
    print(select_ref(override=override))


if __name__ == '__main__':
    main()
