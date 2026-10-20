#!/usr/bin/env python3
"""Reject tracked or non-ignored untracked source changes after packaging."""
import argparse
from pathlib import Path
import subprocess


def source_status(source):
    return subprocess.check_output([
        'git', '-C', str(source), 'status', '--porcelain=v1',
        '--untracked-files=all', '--ignored=no'], text=True)


def require_clean_source(source):
    status = source_status(source)
    if status:
        raise ValueError('Source contains tracked or non-ignored untracked changes:\n' + status)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    require_clean_source(parser.parse_args().source)
    print('Tracked and non-ignored untracked source checks passed')
