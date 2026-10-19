#!/usr/bin/env python3
"""Test newly built native releases; technical evidence remains in CI artifacts."""
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from backfill_package import verify as verify_package
from backfill_verify import (EXECUTABLES, audit_native, bundle_mac, cli_help, digest,
                             install_legacy_fonts, minimum_macos, privacy_scan,
                             python_smoke, run)
from native_plan import REQUIRED_CHECKS, asset_name, validate_source


# Cross-process contract for the version-independent AngelScript boundary smoke.
# Python checks the actual Unicode directory entry, so a legacy Windows code-page
# roundtrip cannot hide a file created under a different, mojibake filename.
BOUNDARY_MODEL_FILENAME = 'Wing Design 100% 中文.vsp3'
BOUNDARY_MODEL_NAMES = (
    'Wing', 'Fuselage', 'CG', 'Pod_3', '主翼', '用户模型_7',
    'Export', 'Cancel', '机翼', '取消', 'Wing &amp; Body',
    'Wing / Fuselage: Export_100%', '@b@.Wing|Left:Right', 'Wing&Body_1',
)


def verify_boundary_output(directory):
    model = Path(directory) / BOUNDARY_MODEL_FILENAME
    if not model.is_file() or model.is_symlink():
        raise ValueError('Native model did not preserve the exact Unicode filename')
    try:
        root = ET.fromstring(model.read_bytes())
    except ET.ParseError as error:
        raise ValueError('Native boundary model is not valid XML') from error
    names = [node.text or '' for node in root.findall('Vehicle/Geom/ParmContainer/Name')]
    if sorted(names) != sorted(BOUNDARY_MODEL_NAMES):
        raise ValueError('Persisted model names differ from the boundary smoke contract')
    return dict(unicode_filename='verified', persisted_names=len(names), xml='verified')


def audit_windows(root, architecture):
    import pefile
    if architecture != 'x86_64':
        raise ValueError('Only native Windows x64 is supported')
    records = []
    packaged = {p.name.lower(): p for p in root.rglob('*') if p.is_file() and p.suffix.lower() == '.dll'}
    system = Path(os.environ['SystemRoot']) / 'System32'
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in ('.exe', '.dll', '.pyd'):
            continue
        binary = pefile.PE(str(path), fast_load=True)
        if binary.FILE_HEADER.Machine != 0x8664:
            raise ValueError('Unexpected PE architecture: ' + path.name)
        binary.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
                                                   pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT']])
        imports = sorted({entry.dll.decode('ascii') for attr in ('DIRECTORY_ENTRY_IMPORT', 'DIRECTORY_ENTRY_DELAY_IMPORT')
                          for entry in getattr(binary, attr, [])})
        binary.close()
        for library in imports:
            key = library.lower()
            if key in packaged or key.startswith(('api-ms-win-', 'ext-ms-win-')) or (system / library).is_file():
                continue
            if re.fullmatch(r'python3\d+\.dll', key) and (Path(sys.base_prefix) / library).is_file():
                continue
            raise ValueError('Unresolved Windows runtime dependency: ' + library)
        records.append({'file': path.relative_to(root).as_posix(), 'type': 'PE32+ AMD64', 'dependencies': imports})
    names = {r['file'] for r in records}
    if not all(name + '.exe' in names for name in EXECUTABLES):
        raise ValueError('Missing Windows executable')
    if not any(Path(name).name.startswith('_vsp.') for name in names):
        raise ValueError('Windows Python extension was omitted')
    return records


def fresh_requirements(root, version, scratch, env):
    # Building wheels is allowed to create metadata only in this disposable copy.
    installation = Path(scratch) / 'install-source'
    shutil.copytree(root / 'python', installation)
    requirements = installation / 'requirements.txt'
    if 'numpy==1.26.4' not in requirements.read_text(encoding='utf-8'):
        raise ValueError('Packaged requirements do not pin the build NumPy ABI')
    venv = Path(scratch) / 'runtime-venv'
    subprocess.run([sys.executable, '-m', 'venv', str(venv)], check=True, env=env, timeout=180)
    interpreter = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    subprocess.run([str(interpreter), '-m', 'pip', 'install', '--disable-pip-version-check', '-r', 'requirements.txt'],
                   cwd=installation, check=True, env=env, timeout=1800)
    subprocess.run([str(interpreter), '-m', 'pip', 'check'], check=True, env=env, timeout=180)
    code = ('import json,numpy,openvsp,sys; '
            'print(json.dumps(dict(version=openvsp.GetVSPVersion(),numpy=numpy.__version__, '
            'python=sys.version.split()[0],module=openvsp.__file__)))')
    checked = json.loads(run(interpreter, '-c', code, cwd=scratch, env=env).strip().splitlines()[-1])
    if version not in checked['version'] or checked['numpy'] != '1.26.4':
        raise ValueError('Fresh requirements installation imports the wrong ABI/version')
    installed = Path(checked.pop('module')).parent
    if not installed.is_relative_to(venv):
        raise ValueError('Import escaped the fresh runtime venv')
    extensions = python_smoke(installed, version, scratch, env, interpreter=interpreter)
    return dict(**checked, pip_check='passed', extensions=extensions)


def make_archive(root, archive):
    if os.name == 'nt':
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for path in sorted(root.rglob('*')):
                if path.is_file():
                    z.write(path, root.name + '/' + path.relative_to(root).as_posix())
    else:
        run('zip', '-q', '-r', '-y', archive, root.name, cwd=root.parent)


def main():
    stage, source, output = map(lambda x: Path(x).resolve(), sys.argv[1:])
    source_sha, tag = os.environ['BACKFILL_SHA'], os.environ['BACKFILL_TAG']
    version = validate_source(source, source_sha, tag)
    roots = list(stage.iterdir())
    if len(roots) != 1 or not roots[0].is_dir():
        raise ValueError('Expected one extracted package root')
    root = roots[0]
    mac, windows = sys.platform == 'darwin', os.name == 'nt'
    native_platform, arch = os.environ['BACKFILL_PLATFORM'], os.environ['BACKFILL_ARCH']
    expected_python = os.environ['BACKFILL_PYTHON']
    if '.'.join(map(str, sys.version_info[:2])) != expected_python:
        raise ValueError('Build interpreter does not match package contract')
    notices = {}
    if mac:
        # One closure is shared by CLI binaries and the installable Python package.
        # Keep it inside the module so pip's wheel relocation remains self-contained.
        module = root / 'python/openvsp/openvsp'
        _, notices = bundle_mac(root, destination=module / 'lib')
        if (root / 'third-party-licenses').exists():
            shutil.copytree(root / 'third-party-licenses', module / 'third-party-licenses', dirs_exist_ok=True)
        shutil.copyfile(root / 'third-party-dependencies.json', module / 'third-party-dependencies.json')
    fonts = install_legacy_fonts(root, version, not (mac or windows))
    records = audit_windows(root, arch) if windows else audit_native(root, arch, mac)
    minimum = minimum_macos(records, platform.mac_ver()[0], native_platform) if mac else None
    diagnostics = Path(os.environ['GITHUB_WORKSPACE']) / 'diagnostics'
    with tempfile.TemporaryDirectory(prefix='openvsp-smoke-') as temp:
        scratch = Path(temp)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
        for key in ('DISPLAY', 'DYLD_LIBRARY_PATH', 'LD_LIBRARY_PATH', 'PYTHONPATH', 'PYTHONHOME'):
            env.pop(key, None)
        # A clean home also prevents a developer's CustomScripts masking missing resources.
        clean_home = scratch / 'home'; clean_home.mkdir()
        env.update(HOME=str(clean_home), USERPROFILE=str(clean_home))
        suffix = '.exe' if windows else ''
        cli = cli_help(root / ('vsp' + suffix), version, scratch, env, diagnostics, not (mac or windows))
        scripts = (
            ('backfill_smoke.as', 'LOCALIZATION_SMOKE_PASS', 'LOCALIZATION_SMOKE_FAIL'),
            ('localization_boundary_smoke.as', 'LOCALIZATION_BOUNDARIES_PASS', 'LOCALIZATION_BOUNDARIES_FAIL'),
            ('localization_resources_smoke.as', 'LOCALIZATION_RESOURCES_PASS', 'LOCALIZATION_RESOURCES_FAIL'),
        )
        for name, success, failure in scripts:
            script = source / 'scripts' / name
            if not script.is_file():
                raise ValueError('Missing mandatory release smoke script: ' + name)
            text = run(root / ('vspscript' + suffix), '-script', script, cwd=scratch, env=env)
            if success not in text or failure in text:
                raise ValueError('Packaged smoke failed: ' + name)
        boundary_file = verify_boundary_output(scratch)
        extensions = python_smoke(root, version, scratch, env)
        installed = fresh_requirements(root, version, scratch, env)
        if not (mac or windows):
            gui = Path(os.environ['GITHUB_WORKSPACE']) / 'gui-input'; gui.mkdir(exist_ok=True)
            shutil.copyfile(scratch / 'localization-smoke.vsp3', gui / 'localization-smoke.vsp3')
    prefixes = []
    for value in (os.environ['GITHUB_WORKSPACE'], str(Path.home())):
        for variant in (value, value.replace('\\', '/'), value.replace('/', '\\')):
            prefixes.extend([variant.encode(), variant.encode('utf-16le')])
    privacy_scan(root, prefixes, diagnostics, mac)
    output.mkdir(parents=True, exist_ok=True)
    name = asset_name(version, native_platform)
    archive = output / name
    make_archive(root, archive)
    source_files = verify_package(archive, source, runtime_resources=True)
    with zipfile.ZipFile(archive) as z:
        if z.testzip():
            raise ValueError('Final ZIP integrity failure')
    clean = not run('git', '-C', source, 'status', '--porcelain', '--untracked-files=no').strip()
    if not clean:
        raise ValueError('Package generation modified tracked source files')
    report = dict(schema=2, tag=tag, source_sha=source_sha, version=version,
                  platform=native_platform, architecture=arch, python=expected_python,
                  workflow_sha=os.environ['GITHUB_SHA'], run_id=os.environ['GITHUB_RUN_ID'],
                  archive=name, sha256=digest(archive), bytes=archive.stat().st_size,
                  checks=sorted(REQUIRED_CHECKS), native=records, third_party_licenses=notices,
                  cli_help=cli, python_extensions=extensions, requirements_install=installed,
                  filesystem_boundary=boundary_file,
                  macos_minimum=minimum, legacy_gui_fonts=fonts, verified_source_files=source_files,
                  source_tracked_files_clean=clean,
                  source_worktree_clean=not run('git', '-C', source, 'status', '--porcelain').strip(),
                  gui_review='pending visual review; screenshots alone do not establish acceptance',
                  macos_signing='ad-hoc only; not Developer ID signed or notarized' if mac else None)
    (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Native checks passed for {name}; SHA-256 {report["sha256"]}; GUI review remains pending')


if __name__ == '__main__':
    main()
