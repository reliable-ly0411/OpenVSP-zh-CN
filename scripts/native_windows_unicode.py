#!/usr/bin/env python3
"""Bounded Windows Unicode diagnostics, using generated fixtures only."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from native_functional import (CLI_BASENAME, CLI_INPUT_SUFFIXES, PASS_MARKERS,
                               STL_FILENAME, FunctionalCheckError, validate_stl,
                               verify_cli_history, verify_functional_outputs)
from native_verify import BOUNDARY_MODEL_FILENAME, verify_boundary_output

SOURCE_BASELINE = '1d6b0b6078716db5854ff04a92610aa58956a0c6'
SOURCE_PATCH_SHA256 = 'ec82cf9335c8d75943884b263b47affe91394fa8539f523e9daa8f40fe134048'
EXPECTED = dict(ascii='Export 100% &.stl', unicode=STL_FILENAME,
                nonbmp='Export 🚀 100% &.stl', absolute='目录 100%/Absolute 中文.stl', blocked='blocked.stl',
                directory='目录 100%/Export 中文.stl', missing='not-created/export.stl')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def path_record(directory, name):
    path = Path(directory) / name
    result = dict(name=name, utf8_hex=name.encode('utf-8').hex(),
                  utf16le_hex=name.encode('utf-16le').hex())
    try:
        info = path.stat()
        result.update(exists=True, file=path.is_file(), bytes=info.st_size)
    except OSError as error:
        result.update(exists=False, errno=error.errno, winerror=getattr(error, 'winerror', None))
    return result


def directory_records(directory):
    # Isolated, script-generated names only; no parent paths or environment dump.
    return [path_record(directory, p.relative_to(directory).as_posix())
            for p in sorted(Path(directory).rglob('*'))][:100]


def redact(text, roots):
    # Keep genuine bounded output and its raw digest, while removing machine paths.
    for root in sorted({str(p) for p in roots if p}, key=len, reverse=True):
        for spelling in (root, root.replace('\\', '/'), root.replace('/', '\\')):
            text = text.replace(spelling, '<fixture-root>')
    return text


def capture(command, directory, roots=()):
    try:
        process = subprocess.run([str(x) for x in command], cwd=directory,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 timeout=240, env=dict(os.environ, OMP_NUM_THREADS='1'))
        code, stdout, stderr, error = process.returncode, process.stdout, process.stderr, None
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr, error = None, exc.stdout or b'', exc.stderr or b'', 'timeout'
    except OSError as exc:
        code, stdout, stderr, error = None, b'', b'', dict(errno=exc.errno, winerror=getattr(exc, 'winerror', None))
    roots = (*roots, directory, Path.home(), os.environ.get('GITHUB_WORKSPACE'),
             os.environ.get('TEMP'), os.environ.get('TMP'))
    record = dict(exit_code=code, error=error, output_origin='actual subprocess capture')
    for label, data in (('stdout', stdout), ('stderr', stderr)):
        record[label] = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                             truncated=len(data) > 16384,
                             text=redact(data[:16384].decode('utf-8', errors='replace'), roots))
    return record, stdout.decode('utf-8', errors='replace') + stderr.decode('utf-8', errors='replace')


def codepages():
    if os.name != 'nt':
        return dict(platform='non-Windows', acp=None, oem=None)
    return dict(platform='Windows', acp=ctypes.windll.kernel32.GetACP(),
                oem=ctypes.windll.kernel32.GetOEMCP())


def probe(executable):
    report = dict(schema=1, kind='crt-path-comparison', environment=codepages(), cases=[])
    for mode in ('narrow', 'utf8'):
        for case in ('ascii', 'unicode', 'directory', 'absolute', 'nonbmp', 'blocked', 'missing') + (('invalid',) if os.name == 'nt' else ()):
            with tempfile.TemporaryDirectory(prefix='vsp-unicode-crt-') as name:
                work = Path(name)
                (work / '目录 100%').mkdir()
                (work / 'blocked.stl').mkdir()
                result, output = capture([executable, mode, case], work, [executable.parent])
                result.update(mode=mode, case=case, files=directory_records(work))
                if result['exit_code'] != 0:
                    raise ValueError('CRT probe process did not finish')
                result['crt'] = json.loads(output)
                if case in EXPECTED:
                    result['expected'] = path_record(work, EXPECTED[case])
                report['cases'].append(result)
    fixed = [r for r in report['cases'] if r['mode'] == 'utf8']
    report['passed'] = all(
        (r['expected']['exists'] and r['crt']['write_ok'] and r['crt']['close_result'] == 0)
        if r['case'] in ('ascii', 'unicode', 'directory', 'absolute', 'nonbmp') else
        (not r['crt']['opened'] and r['crt']['open_errno'] != 0)
        if r['case'] in ('missing', 'blocked') or os.name == 'nt' else True for r in fixed)
    return report


def validate_case(case, work):
    if case == 'boundary':
        return verify_boundary_output(work)
    if case == 'functional':
        return verify_functional_outputs(work)
    return {name: validate_stl((work / name).read_bytes()) for name in
            ('Tagged 100% 中文.stl', '目录 100%/Export 中文.stl', 'Export 100%.stl')}


def package(package_root, source, phase):
    executables = list(package_root.rglob('vspscript.exe' if os.name == 'nt' else 'vspscript'))
    if len(executables) != 1:
        raise ValueError('Expected exactly one packaged vspscript')
    exe = executables[0].resolve()
    report = dict(schema=1, kind='native-package-unicode', phase=phase,
                  environment=codepages(), executable_sha256=digest(exe), cases=[])
    scripts = Path(__file__).resolve().parent
    fixtures = (
        ('boundary', source / 'scripts/localization_boundary_smoke.as', ['LOCALIZATION_BOUNDARIES_PASS']),
        ('functional', scripts / 'native_functional_smoke.as', PASS_MARKERS),
        ('stl-variants', scripts / 'native_unicode_stl_smoke.as', ['NATIVE_UNICODE_STL_PASS']))
    for case, script, markers in fixtures:
        with tempfile.TemporaryDirectory(prefix='vsp-unicode-package-') as name:
            work = Path(name)
            (work / '目录 100%').mkdir()
            result, output = capture([exe, '-script', script], work, [exe.parent, source, scripts])
            result.update(case=case, script_sha256=digest(script), files=directory_records(work),
                          markers_passed=all(m in {line.strip() for line in output.splitlines()} for m in markers) and 'FAIL' not in output)
            expected = BOUNDARY_MODEL_FILENAME if case == 'boundary' else STL_FILENAME
            if case != 'stl-variants':
                result['expected'] = path_record(work, expected)
            try:
                result['validation'] = validate_case(case, work)
                result['disk_passed'] = True
            except (ValueError, OSError) as error:
                result['disk_passed'] = False
                result['disk_error'] = (error.category if isinstance(error, FunctionalCheckError)
                                        else type(error).__name__)
            result['passed'] = result['exit_code'] == 0 and result['markers_passed'] and result['disk_passed']
            # Preserve the independent direct-solver test from the production gate.
            if case == 'functional':
                cli = work / 'direct-cli'; cli.mkdir()
                inputs = [work / (CLI_BASENAME + suffix) for suffix in CLI_INPUT_SUFFIXES]
                if all(p.is_file() for p in inputs):
                    for p in inputs: shutil.copyfile(p, cli / p.name)
                    cli_record, cli_output = capture(
                        [exe.with_name('vspaero.exe' if os.name == 'nt' else 'vspaero'), '-omp', '1', CLI_BASENAME],
                        cli, [exe.parent, source, scripts])
                    try:
                        cli_record['validation'] = verify_cli_history(cli)
                        cli_record['passed'] = cli_record['exit_code'] == 0 and 'FAIL' not in cli_output
                    except (ValueError, OSError):
                        cli_record['passed'] = False
                    result['direct_solver'] = cli_record
                    result['passed'] = result['passed'] and cli_record['passed']
                else:
                    result['passed'] = False
                    result['direct_solver'] = dict(passed=False, reason='input-missing')
            report['cases'].append(result)
    report['passed'] = all(case['passed'] for case in report['cases'])
    return report


def apply_patch(source, tooling):
    before = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if before != SOURCE_BASELINE:
        raise ValueError('The diagnostic requires the pinned 3.55 baseline')
    if subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain', '--untracked-files=no']).strip():
        raise ValueError('Baseline tracked source is not clean')
    patch = (tooling / 'scripts/windows_unicode_stl.patch').read_bytes()
    if hashlib.sha256(patch).hexdigest() != SOURCE_PATCH_SHA256:
        raise ValueError('Pinned minimal patch content changed')
    subprocess.run(['git', '-C', str(source), 'apply', '--check', '-'], input=patch, check=True)
    subprocess.run(['git', '-C', str(source), 'apply', '-'], input=patch, check=True)
    subprocess.run(['git', '-C', str(source), 'diff', '--check'], check=True)
    paths = ['src/geom_core/Vehicle.cpp', 'src/util/FileUtil.h']
    changed = subprocess.check_output(['git', '-C', str(source), 'diff', '--name-only'], text=True).splitlines()
    if sorted(changed) != paths:
        raise ValueError('Unexpected source file changed')
    subprocess.run(['git', '-C', str(source), 'add', '--', *paths], check=True)
    subprocess.run(['git', '-C', str(source), '-c', 'user.name=OpenVSP diagnostic',
                    '-c', 'user.email=noreply@users.noreply.github.com', 'commit',
                    '-m', 'Diagnostic-only UTF-8 STL path comparison'], check=True)
    commit, tree, parent = subprocess.check_output(
        ['git', '-C', str(source), 'show', '-s', '--format=%H%n%T%n%P', 'HEAD'], text=True).splitlines()
    if parent != before or subprocess.check_output(
            ['git', '-C', str(source), 'status', '--porcelain', '--untracked-files=no']).strip():
        raise ValueError('Temporary diagnostic source is not a clean child of the baseline')
    return dict(schema=1, baseline=before, temporary_source_sha=commit, temporary_tree=tree,
                temporary_parent=parent, diagnostic_only=True, promotion_eligible=False,
                patch_sha256=hashlib.sha256(patch).hexdigest(), changed_files=paths)


def compare(baseline, patched):
    if baseline['phase'] != 'baseline' or patched['phase'] != 'patched':
        raise ValueError('Wrong comparison phases')
    old = next(c for c in baseline['cases'] if c['case'] == 'functional')
    # An expected failure only counts if we have actual process and directory evidence.
    if (old['exit_code'] != 0 or not old['markers_passed'] or old.get('disk_error') != 'stl-file-missing'
            or old['expected']['exists'] or not old['stdout']['bytes']):
        raise ValueError('Baseline does not reproduce the diagnosed failure')
    if not next(c for c in baseline['cases'] if c['case'] == 'boundary')['passed']:
        raise ValueError('Baseline model-name regression did not pass')
    acp = baseline['environment']['acp']
    if not acp or acp == 65001:
        raise ValueError('Baseline requires a measured non-UTF-8 Windows ACP')
    mojibake = STL_FILENAME.encode('utf-8').decode('cp' + str(acp))
    if not any(f['name'] == mojibake and f['file'] and f['bytes'] > 0 for f in old['files']):
        raise ValueError('Missing native directory evidence of the ACP filename mismatch')
    if not patched['passed'] or baseline['executable_sha256'] == patched['executable_sha256']:
        raise ValueError('Patched package did not pass all gates or was not rebuilt')
    return dict(schema=1, baseline_failure='UTF-8 bytes interpreted by Windows ACP',
                exact_mojibake_directory_entry_verified=True, patched_all_gates_passed=True,
                baseline_executable_sha256=baseline['executable_sha256'],
                patched_executable_sha256=patched['executable_sha256'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('crt'); p.add_argument('--executable', type=Path, required=True)
    p = sub.add_parser('package'); p.add_argument('--package', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True); p.add_argument('--phase', choices=('baseline', 'patched'), required=True)
    p = sub.add_parser('apply'); p.add_argument('--source', type=Path, required=True); p.add_argument('--tooling', type=Path, required=True)
    p = sub.add_parser('compare'); p.add_argument('--baseline', type=Path, required=True); p.add_argument('--patched', type=Path, required=True)
    for p in sub.choices.values(): p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'crt': report = probe(args.executable.resolve())
    elif args.command == 'package': report = package(args.package.resolve(), args.source.resolve(), args.phase)
    elif args.command == 'apply': report = apply_patch(args.source.resolve(), args.tooling.resolve())
    else: report = compare(json.loads(args.baseline.read_text()), json.loads(args.patched.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    print(args.command + ': evidence saved; all required gates ' + ('passed' if report.get('passed', True) else 'did not pass'))
    if args.command == 'crt' or (args.command == 'package' and args.phase == 'patched'):
        if not report['passed']: raise SystemExit(1)


if __name__ == '__main__': main()
