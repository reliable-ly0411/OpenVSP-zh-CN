#!/usr/bin/env python3
"""Verify CI-built native ZIPs, relocate macOS dylibs, emit review-only artifacts.

Only the CI runner executes its own just-built executables. This script is not a
validator for arbitrary downloaded binaries. No uploads or Release mutations.
"""
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from backfill_diagnostics import macho_regions, summarize_matches, symbol_categories

SYSTEM_MAC = ('/usr/lib/', '/System/Library/')
EXECUTABLES = ('vsp', 'vspscript', 'vspaero', 'vspviewer', 'vsploads')
SECRET = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')


def run(*args, **kwargs):
    return subprocess.check_output([str(a) for a in args], text=True, stderr=subprocess.STDOUT,
                                   timeout=120, **kwargs)



def cli_help(executable, version, scratch, env, diagnostics, linux):
    """Never accept a failed help command; exact old X11 startup error may retry in Xvfb."""
    evidence = {'display': 'none', 'initial_exit_code': 0}
    def unavailable(exc, phase):
        category = 'timeout' if isinstance(exc, subprocess.TimeoutExpired) else 'launcher-unavailable'
        diagnostics.mkdir(parents=True, exist_ok=True)
        (diagnostics/'runtime.json').write_text(json.dumps({
            'schema': 1, 'command': 'vsp-help', 'phase': phase, 'category': category,
            'contains_output_values': False, 'binary_uploaded': False}, indent=2) + '\n')
        raise ValueError('Packaged CLI help unavailable; see value-free runtime diagnosis') from None
    try:
        text = run(executable, '-help', cwd=scratch, env=env)
    except (subprocess.TimeoutExpired, OSError) as exc:
        unavailable(exc, 'initial')
    except subprocess.CalledProcessError as exc:
        output = exc.output or ''
        category = 'x11-display-unavailable' if output.strip() == "Can't open display:" else 'unclassified-runtime-failure'
        evidence = {'display': 'none', 'initial_exit_code': exc.returncode, 'initial_category': category}
        diagnostics.mkdir(parents=True, exist_ok=True)
        report = {'schema': 1, 'command': 'vsp-help', 'exit_code': exc.returncode,
                  'category': category, 'contains_output_values': False, 'binary_uploaded': False}
        (diagnostics/'runtime.json').write_text(json.dumps(report, indent=2) + '\n')
        if not (linux and version in ('3.51.2', '3.51.3') and exc.returncode == 1 and category == 'x11-display-unavailable'):
            raise ValueError('Packaged CLI help failed; see value-free runtime diagnosis') from None
        # Historical icon setup opens X11 before batchMode. Keep source immutable.
        try:
            text = run('xvfb-run', '-a', '--server-args=-screen 0 1600x1000x24',
                       executable, '-help', cwd=scratch, env=env)
        except (subprocess.TimeoutExpired, OSError) as exc:
            unavailable(exc, 'xvfb-retry')
        except subprocess.CalledProcessError as retry:
            report['xvfb_retry_exit_code'] = retry.returncode
            (diagnostics/'runtime.json').write_text(json.dumps(report, indent=2) + '\n')
            raise ValueError('Packaged CLI help also failed with Xvfb') from None
        evidence['display'] = 'Xvfb retry after exact X11 display-unavailable error'
        evidence['retry_exit_code'] = 0
    if '用法' not in text:
        raise ValueError('Packaged Chinese CLI help failed')
    return evidence


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def machos(root):
    return [p for p in root.rglob('*') if p.is_file() and 'Mach-O' in run('file', '-b', p)]


def rpaths(path):
    return re.findall(r'cmd LC_RPATH\s+cmdsize \d+\s+path (.+?) \(offset', run('otool', '-l', path))


def dependencies(path):
    ids = run('otool', '-D', path).splitlines()[1:]
    return [line.strip().split(' (compatibility version')[0]
            for line in run('otool', '-L', path).splitlines()[1:]
            if line.strip().split(' (compatibility version')[0] not in ids]


def is_inside(path, root):
    return path.resolve().is_relative_to(root.resolve())


def bundle_mac(root):
    """Copy the complete non-system dylib closure and use loader-relative links."""
    initial = machos(root)
    original_rpaths = {p: rpaths(p) for p in initial}
    extra_rpaths = sorted({r for rs in original_rpaths.values() for r in rs if r.startswith('/')})
    destination = root / 'lib'
    destination.mkdir(exist_ok=True)
    seen = {}
    queue = [(p, p) for p in initial]
    graph = []
    notices = {}
    while queue:
        target, original = queue.pop(0)
        original_paths = rpaths(original)
        edges = []
        for dep in dependencies(original):
            if dep.startswith(SYSTEM_MAC):
                edges.append(dep)
                continue
            if '.framework/' in dep:
                raise ValueError('Non-system frameworks require a dedicated bundle implementation')
            def expand(value):
                return value.replace('@loader_path', str(original.parent)).replace('@executable_path', str(root))
            if dep.startswith('@rpath/'):
                candidates = [Path(expand(r)) / dep.removeprefix('@rpath/')
                              for r in original_paths + extra_rpaths]
            else:
                candidates = [Path(expand(dep))]
            matches = {p.resolve() for p in candidates if p.is_file()}
            if len(matches) != 1:
                raise ValueError(f'Unresolved or ambiguous dependency in {target.name}: {dep}')
            source = matches.pop()
            if any(part.endswith('.framework') for part in source.parts):
                raise ValueError('Non-system framework symlink targets are not supported')
            if is_inside(source, root):
                copied = source
            else:
                key = str(source)
                if key not in seen:
                    # Prefix avoids collisions from different Homebrew formulae.
                    copied = destination / (digest(source)[:12] + '-' + source.name)
                    shutil.copy2(source, copied)
                    copied.chmod(copied.stat().st_mode | 0o200)
                    seen[key] = copied
                    queue.append((copied, source))
                    # Preserve license/notice files shipped with the installed formula.
                    cellar = next((p for p in source.parents if (p/'INSTALL_RECEIPT.json').is_file()), None)
                    if cellar:
                        formula = cellar.parent.name
                        notice_dir = root / 'third-party-licenses' / formula
                        notice_dir.mkdir(parents=True, exist_ok=True)
                        found = []
                        for p in cellar.rglob('*'):
                            if p.is_file() and p.name.upper().startswith(('LICENSE', 'COPYING', 'NOTICE', 'COPYRIGHT')):
                                rel = p.relative_to(cellar)
                                dest = notice_dir / rel
                                dest.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copyfile(p, dest)
                                found.append(rel.as_posix())
                        notices[formula] = {'license_files': sorted(found),
                                            'formula': f'https://formulae.brew.sh/formula/{formula}'}
                    else:
                        notices[source.name] = {'license_files': [], 'origin': 'Needs manual license review'}
                copied = seen[key]
            replacement = '@loader_path/' + os.path.relpath(copied, target.parent)
            run('install_name_tool', '-change', dep, replacement, target)
            edges.append(replacement)
        if target.suffix == '.dylib':
            run('install_name_tool', '-id', '@loader_path/' + target.name, target)
        for path in rpaths(target):
            # All non-system dependencies were made explicit loader-relative paths.
            run('install_name_tool', '-delete_rpath', path, target)
        graph.append({'file': target.relative_to(root).as_posix(), 'dependencies': edges})
    for p in machos(root):
        # Mach-O N_OSO/debug-map entries can retain linker object paths even with
        # compiler prefix maps. Remove debug symbols only, retaining runtime exports.
        # This must happen before ad-hoc signing; all smoke/privacy checks run after it.
        run('strip', '-S', p)
        run('codesign', '--force', '--sign', '-', p)
        run('codesign', '--verify', '--strict', p)
    (root/'third-party-dependencies.json').write_text(json.dumps(notices, indent=2) + '\n')
    return graph, notices


def privacy_scan(root, private_prefixes, diagnostic_dir=None, mac=False):
    """Fail without echoing matched secrets or their values to public CI logs."""
    for p in root.rglob('*'):
        if p.is_symlink() and not is_inside(p, root):
            raise ValueError('Package contains an escaping symlink')
        if not p.is_file():
            continue
        data = p.read_bytes()
        if SECRET.search(data):
            raise ValueError(f'Credential-like content in packaged file: {p.relative_to(root)}')
        if any(prefix and prefix in data for prefix in private_prefixes):
            if diagnostic_dir is not None:
                report = {'schema': 1, 'rejected_file': p.relative_to(root).as_posix(),
                          'contains_matched_values': False, 'binary_uploaded': False,
                          'compiler_file_prefix_map': '-ffile-prefix-map=' in os.environ.get('CXXFLAGS', ''),
                          'compiler_debug_prefix_map': '-fdebug-prefix-map=' in os.environ.get('CXXFLAGS', ''),
                          'mac_debug_strip_before_signing': mac}
                regions = []
                if mac:
                    try:
                        regions = macho_regions(run('otool', '-l', p))
                        report['symbol_categories'] = symbol_categories(run('nm', '-a', p), private_prefixes)
                    except (subprocess.SubprocessError, OSError, ValueError):
                        report['native_diagnostics'] = 'unavailable'
                toolchain = Path(__file__).with_name('backfill_libxml_toolchain.cmake')
                if mac and os.environ.get('BACKFILL_LIBXML_SYSCONFDIR') == '/etc' and toolchain.is_file():
                    report['libxml_toolchain_sha256'] = digest(toolchain)
                    report['libxml_sysconfdir_requested'] = '/etc'
                report['matches'] = summarize_matches(data, private_prefixes, regions)
                diagnostic_dir.mkdir(parents=True, exist_ok=True)
                (diagnostic_dir/'privacy.json').write_text(json.dumps(report, indent=2) + '\n')
            raise ValueError(f'Runner/workspace path remains in packaged file: {p.relative_to(root)}')
        if p.name in ('.env', '.git-credentials', 'CMakeCache.txt') or '.git' in p.relative_to(root).parts:
            raise ValueError('Build metadata or credentials file found in package')


def audit_native(root, architecture, mac):
    records = []
    for p in sorted(root.rglob('*')):
        if not p.is_file():
            continue
        kind = run('file', '-b', p)
        if ('Mach-O' if mac else 'ELF') not in kind:
            continue
        record = {'file': p.relative_to(root).as_posix(), 'type': kind.strip()}
        if mac:
            if run('lipo', '-archs', p).strip().split() != [architecture]:
                raise ValueError(f'Unexpected Mach-O architecture: {p.name}')
            load = run('otool', '-l', p)
            record['minos'] = parse_minos(load)
            if not record['minos']:
                raise ValueError('Mach-O minimum OS was not recorded')
            record['dependencies'] = dependencies(p)
            record['rpaths'] = rpaths(p)
            for dep in record['dependencies']:
                if dep.startswith(SYSTEM_MAC):
                    continue
                if not dep.startswith('@loader_path/'):
                    raise ValueError('Unrelocated Mach-O dependency')
                resolved = p.parent / dep.removeprefix('@loader_path/')
                if not resolved.is_file() or not is_inside(resolved, root):
                    raise ValueError('Mach-O dependency escapes package or is missing')
            if any(not r.startswith('@loader_path') for r in record['rpaths']):
                raise ValueError('Absolute or unknown macOS RPATH')
        else:
            header = run('readelf', '-h', p)
            if not re.search(r'Machine:\s+AArch64', header):
                raise ValueError(f'Unexpected ELF architecture: {p.name}')
            dyn = run('readelf', '-d', p)
            record['rpaths'] = re.findall(r'\((?:RUNPATH|RPATH)\).*?\[(.*?)\]', dyn)
            for paths in record['rpaths']:
                for path in paths.split(':'):
                    if path and not path.startswith('$ORIGIN'):
                        raise ValueError('Absolute or unknown ELF RPATH')
            # ldd is used only on binaries produced by this CI run.
            linked = run('ldd', p)
            if 'not found' in linked or 'libcminpack.so' in linked:
                raise ValueError('Missing dependency or forbidden system CMINPACK')
            record['needed'] = re.findall(r'\(NEEDED\).*?\[(.*?)\]', dyn)
            record['system_packages'] = []
            for lib in re.findall(r'=> (/\S+)', linked):
                lib_path = Path(lib)
                if is_inside(lib_path, root):
                    continue
                if not str(lib_path).startswith(('/lib/', '/usr/lib/')):
                    raise ValueError('ELF depends on non-system, non-packaged library')
                # Capture distro runtime dependency owners, not ephemeral runner paths.
                result = subprocess.run(['dpkg-query', '-S', str(lib_path)], capture_output=True, text=True)
                if result.returncode:
                    result = subprocess.run(['dpkg-query', '-S', str(lib_path.resolve())], capture_output=True, text=True)
                if result.returncode:
                    raise ValueError(f'Cannot identify runtime dependency owner: {lib_path.name}')
                record['system_packages'].extend(line.split(': /')[0] for line in result.stdout.splitlines())
        records.append(record)
    if not records:
        raise ValueError('No native binaries in package')
    for name in EXECUTABLES:
        if name not in {r['file'] for r in records}:
            raise ValueError(f'Missing native program: {name}')
    if not any(Path(r['file']).name.startswith('_vsp.') for r in records):
        raise ValueError('Python extension was silently omitted')
    return records




def parse_minos(load_commands):
    values = []
    for block in load_commands.split('Load command')[1:]:
        if re.search(r'^\s*cmd LC_BUILD_VERSION\s*$', block, re.MULTILINE):
            values.extend(re.findall(r'^\s*minos ([\d.]+)\s*$', block, re.MULTILINE))
        elif re.search(r'^\s*cmd LC_VERSION_MIN_MACOSX\s*$', block, re.MULTILINE):
            values.extend(re.findall(r'^\s*version ([\d.]+)\s*$', block, re.MULTILINE))
    return values


def version_tuple(value):
    parts = tuple(map(int, value.split('.')))
    return (parts + (0, 0, 0))[:3]


def minimum_macos(records, host_version, platform_name):
    values = [v for record in records for v in record.get('minos', [])]
    if not values:
        raise ValueError('Missing Mach-O minimum OS evidence')
    minimum = max(values, key=version_tuple)
    match = re.match(r'macOS-(\d+)-', platform_name)
    if not match or version_tuple(minimum)[0] > int(match.group(1)):
        raise ValueError('Mach-O minimum OS exceeds named macOS platform')
    if version_tuple(minimum) > version_tuple(host_version):
        raise ValueError('Mach-O minimum OS exceeds actual smoke-test host')
    return {'maximum_macho_minimum': minimum, 'tested_host': host_version,
            'compatibility': 'No support claimed below the maximum Mach-O minimum; only this host was tested'}


def python_smoke(root, expected_version, scratch, env):
    extensions = sorted(p for p in root.rglob('_vsp*.so')
                        if p.name.split('.')[0] in ('_vsp', '_vsp_g'))
    modules = [p.name.split('.')[0] for p in extensions]
    if sorted(modules) != ['_vsp', '_vsp_g']:
        raise ValueError('Expected exactly one _vsp and one _vsp_g extension')
    checks = []
    code = (
        'import importlib.util,json,sys,sysconfig; '
        'spec=importlib.util.spec_from_file_location(sys.argv[2],sys.argv[1]); '
        'module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); '
        'print(json.dumps(dict(version=module.GetVSPVersion(), '
        'interpreter_soabi=sysconfig.get_config_var("SOABI"), python=sys.version.split()[0])))'
    )
    for extension in extensions:
        module = extension.name.split('.')[0]
        checked = json.loads(run(sys.executable, '-c', code, extension, module, cwd=scratch, env=env))
        if expected_version not in checked['version']:
            raise ValueError('Packaged Python ABI/import/version smoke failed')
        checks.append(dict(file=extension.relative_to(root).as_posix(), module=module, **checked))
    return checks


def main():
    stage, source, out = map(lambda s: Path(s).resolve(), sys.argv[1:])
    roots = list(stage.iterdir())
    if len(roots) != 1 or not roots[0].is_dir():
        raise ValueError('Expected one package root')
    root = roots[0]
    mac = sys.platform == 'darwin'
    notices = {}
    if mac:
        _, notices = bundle_mac(root)
    records = audit_native(root, os.environ['BACKFILL_ARCH'], mac)
    macos_minimum = minimum_macos(records, platform.mac_ver()[0], os.environ['BACKFILL_PLATFORM']) if mac else None
    # Clean cwd and relocated install tree catch build-directory-relative dependencies.
    with tempfile.TemporaryDirectory() as scratch:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for key in ('DISPLAY', 'DYLD_LIBRARY_PATH', 'LD_LIBRARY_PATH', 'PYTHONPATH'):
            env.pop(key, None)
        cli_evidence = cli_help(root/'vsp', os.environ['BACKFILL_VERSION'], scratch, env,
                                Path(os.environ['GITHUB_WORKSPACE'])/'diagnostics', not mac)
        smoke = run(root/'vspscript', '-script', Path(__file__).with_name('backfill_smoke.as'), cwd=scratch, env=env)
        if 'LOCALIZATION_SMOKE_PASS' not in smoke or 'LOCALIZATION_SMOKE_FAIL' in smoke:
            raise ValueError('Packaged model localization smoke failed')
        python_checks = python_smoke(root, os.environ['BACKFILL_VERSION'], scratch, env)
        if not mac:
            # Keep only the already-validated synthetic model for optional GUI capture.
            # This directory is outside the package and is never included in its ZIP.
            gui_input = Path(os.environ['GITHUB_WORKSPACE'])/'gui-input'
            try:
                gui_input.mkdir(exist_ok=True)
                shutil.copyfile(Path(scratch)/'localization-smoke.vsp3', gui_input/'localization-smoke.vsp3')
            except OSError:
                print('Optional GUI model preparation unavailable; package verification continues.')
    workspace = os.environ['GITHUB_WORKSPACE'].encode()
    home = os.environ['HOME'].encode()
    privacy_scan(root, [workspace, home], Path(os.environ['GITHUB_WORKSPACE'])/'diagnostics', mac)
    out.mkdir(exist_ok=True)
    name = f"OpenVSP-{os.environ['BACKFILL_VERSION']}-{os.environ['BACKFILL_PLATFORM']}-zh-CN.zip"
    archive = out/name
    # System zip preserves UNIX modes and symlinks; do not ship the original unrelocated ZIP.
    run('zip', '-q', '-r', '-y', archive, root.name, cwd=stage)
    run(sys.executable, Path(__file__).with_name('backfill_package.py'), archive, source, cwd=source)
    with zipfile.ZipFile(archive) as z:
        if z.testzip():
            raise ValueError('Final ZIP integrity failure')
    report = {
        'schema': 1, 'tag': os.environ['BACKFILL_TAG'], 'source_sha': os.environ['BACKFILL_SHA'],
        'version': os.environ['BACKFILL_VERSION'], 'platform': os.environ['BACKFILL_PLATFORM'],
        'architecture': os.environ['BACKFILL_ARCH'], 'python': os.environ['BACKFILL_PYTHON'],
        'workflow_sha': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
        'archive': name, 'sha256': digest(archive), 'bytes': archive.stat().st_size,
        'packaging_changes': ['AGENTS.md supplemented from historical source if absent',
                              'macOS non-system dylibs bundled with loader-relative links; debug symbols stripped before ad-hoc signing' if mac else 'No ELF dependency rewriting'],
        'checks': ['native architecture', 'dependency closure / RPATH', 'Chinese CLI help',
                   'AngelScript model smoke', 'Python extension import/version',
                   'source examples/help/documents byte equality', 'ZIP integrity', 'privacy scan'],
        'native': records, 'third_party_licenses': notices,
        'cli_help': cli_evidence, 'python_extensions': python_checks, 'macos_minimum': macos_minimum,
        'publication_ready': False,
        'pending_review': ['GUI/font rendering on actual target platform',
                           'Third-party redistribution licenses and runtime requirements',
                           'Separate explicit release attachment approval'],
        'source_worktree_clean': True,
        'libxml_toolchain_sha256': digest(Path(__file__).with_name('backfill_libxml_toolchain.cmake')) if mac and os.environ.get('BACKFILL_LIBXML_SYSCONFDIR') == '/etc' else None,
        'libxml_sysconfdir_mode': os.environ.get('BACKFILL_LIBXML_SYSCONFDIR', 'system-library'),
        'macos_signing': 'Local ad-hoc signature only; not Developer ID signed or notarized' if mac else None,
    }
    # No logs or environment dumps are exported. Reports have only curated fields.
    (out/'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f'Verified candidate: {name}; SHA-256 {report["sha256"]}; publication requires separate review')

if __name__ == '__main__':
    main()
