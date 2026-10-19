#!/usr/bin/env python3
"""Require a native Homebrew LLVM bottle, then record the actual compiler."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess


def command(*args):
    return subprocess.check_output(args, text=True, timeout=120).strip()


def bottle_contract(data, target, architecture, llvm, host_version):
    match = re.fullmatch(r'macOS-(14|15)-(arm64|x86_64)-Python3\.11', target)
    if not match or match[2] != architecture or host_version.split('.')[0] != match[1]:
        raise ValueError('Actual macOS host/architecture must match the named native target')
    if llvm != '16':
        raise ValueError('This reviewed native macOS matrix requires LLVM 16')
    formula_name = 'llvm@' + llvm
    formulae = [f for f in data.get('formulae', []) if f.get('name') == formula_name]
    if len(formulae) != 1:
        raise ValueError('Expected exactly one official LLVM formula')
    formula = formulae[0]
    if formula.get('tap') != 'homebrew/core' or formula.get('disabled'):
        raise ValueError('LLVM formula is not an enabled official Homebrew formula')
    version = formula.get('versions', {}).get('stable', '')
    if not re.fullmatch(r'16\.\d+\.\d+', version):
        raise ValueError('Unexpected LLVM stable version')
    os_name = {'14': 'sonoma', '15': 'sequoia'}[match[1]]
    bottle_tag = ('arm64_' if architecture == 'arm64' else '') + os_name
    bottle = formula.get('bottle', {}).get('stable', {}).get('files', {}).get(bottle_tag, {})
    checksum = bottle.get('sha256', '')
    expected_url = 'https://ghcr.io/v2/homebrew/core/llvm/16/blobs/sha256:' + checksum
    if not re.fullmatch(r'[0-9a-f]{64}', checksum) or bottle.get('url') != expected_url:
        raise ValueError('No official LLVM bottle for the exact native macOS host; source-build fallback is forbidden')
    revision = formula.get('revision', 0)
    if not isinstance(revision, int) or revision < 0:
        raise ValueError('Invalid LLVM formula revision')
    return dict(schema=1, platform=target, host_version=host_version, architecture=architecture,
                formula=formula_name, compiler_version=version,
                keg_version=version + (f'_{revision}' if revision else ''),
                bottle_tag=bottle_tag, bottle_sha256=checksum, bottle_url=expected_url)


def verify_install(contract, receipt, keg_version, compilers):
    if receipt.get('poured_from_bottle') is not True or keg_version != contract['keg_version']:
        raise ValueError('Selected LLVM installation is not the planned bottled version')
    if receipt.get('arch', contract['architecture']) != contract['architecture']:
        raise ValueError('LLVM receipt architecture differs from the native target')
    if set(compilers) != {'clang', 'clang++'}:
        raise ValueError('Both actual C and C++ compilers must be verified')
    for name, record in compilers.items():
        version = re.search(r'\bclang version (\d+\.\d+\.\d+)\b', record.get('version', ''))
        if (record.get('architectures') != [contract['architecture']] or not version
                or version[1] != contract['compiler_version']
                or not re.fullmatch(r'[0-9a-f]{64}', record.get('sha256', ''))):
            raise ValueError('Actual compiler architecture/version/hash mismatch: ' + name)
    return dict(contract, installation='verified official bottle receipt', compilers=compilers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('preflight', 'verify'))
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    if platform.system() != 'Darwin' or platform.machine() != os.environ['BACKFILL_ARCH']:
        raise ValueError('Native macOS host architecture was not established')
    if args.phase == 'preflight':
        data = json.loads(command('brew', 'info', '--json=v2', 'llvm@' + os.environ['BACKFILL_LLVM']))
        report = bottle_contract(data, os.environ['BACKFILL_PLATFORM'], os.environ['BACKFILL_ARCH'],
                                 os.environ['BACKFILL_LLVM'], platform.mac_ver()[0])
    else:
        contract = json.loads(args.report.read_text(encoding='utf-8'))
        if contract['host_version'] != platform.mac_ver()[0] or contract['architecture'] != platform.machine():
            raise ValueError('macOS host changed after toolchain preflight')
        prefix = Path(command('brew', '--prefix', contract['formula'])).resolve()
        receipt = json.loads((prefix / 'INSTALL_RECEIPT.json').read_text(encoding='utf-8'))
        compilers = {}
        for name in ('clang', 'clang++'):
            executable = prefix / 'bin' / name
            compilers[name] = dict(version=command(str(executable), '--version').splitlines()[0],
                                   architectures=command('lipo', '-archs', str(executable)).split(),
                                   sha256=hashlib.sha256(executable.read_bytes()).hexdigest())
        report = verify_install(contract, receipt, prefix.name, compilers)
        if summary := os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(summary, 'a', encoding='utf-8') as stream:
                stream.write(f"Native toolchain: {report['platform']}, actual macOS {report['host_version']}, "
                             f"{report['bottle_tag']} bottle.\n")
                for name, record in compilers.items():
                    stream.write(f"- {name}: {record['version']}; {','.join(record['architectures'])}; "
                                 f"SHA-256 {record['sha256']}\n")
    args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
