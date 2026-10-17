#!/usr/bin/env python3
"""Best-effort Linux GUI evidence inside Xvfb; never a release acceptance gate."""
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import time


GUI_INPUT_DIRECTORY = Path("/tmp/openvsp-ui-evidence")

def prepare_model(source):
    # Fresh CI-only neutral path: GUI expands basenames into absolute paths in pixels.
    GUI_INPUT_DIRECTORY.mkdir(exist_ok=False)
    model = GUI_INPUT_DIRECTORY / "localization-smoke.vsp3"
    shutil.copyfile(source, model)
    return model

def gui_executable(root, version):
    return root/('vsp-zh-CN' if version in ('3.51.2', '3.51.3') else 'vsp')


def capture(root, model, output, version='3.53.0'):
    executable = gui_executable(root, version)
    if not executable.is_file() or not model.is_file():
        raise ValueError('Verified package or smoke model missing')
    output.mkdir(parents=True, exist_ok=True)
    screenshot = output/'linux-arm64-main-and-geometry-tree.png'
    process = subprocess.Popen([str(executable), model.name], cwd=model.parent,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        visible = False
        for _ in range(20):
            if process.poll() is not None:
                raise RuntimeError('GUI exited before capture')
            tree = subprocess.check_output(['xwininfo', '-root', '-tree'], text=True, timeout=10)
            if 'OpenVSP' in tree:
                visible = True
                break
            time.sleep(1)
        if not visible:
            raise RuntimeError('OpenVSP window did not appear')
        time.sleep(3)  # Allow initial model redraw/font rendering to settle.
        if process.poll() is not None:
            raise RuntimeError('GUI exited before capture')
        subprocess.run(['import', '-window', 'root', '-strip', str(screenshot)], check=True, timeout=30)
        if not screenshot.is_file() or screenshot.stat().st_size == 0:
            raise RuntimeError('Screenshot was not created')
        return screenshot
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)


def main():
    workspace = Path(os.environ['GITHUB_WORKSPACE'])
    output = workspace/'gui-evidence'
    output.mkdir(exist_ok=True)
    report = {'status': 'not_verified', 'manual_visual_review': 'pending',
              'scope': 'Initial main window and geometry tree only; no wing-page navigation',
              'display': 'Xvfb 1600x1000x24; not a real desktop acceptance test'}
    try:
        roots = list((workspace/'stage').iterdir())
        if len(roots) != 1:
            raise ValueError('Ambiguous package directory')
        model = prepare_model(workspace/'gui-input/localization-smoke.vsp3')
        version = os.environ['BACKFILL_VERSION']
        image = capture(roots[0], model, output, version)
        report['launcher'] = gui_executable(roots[0], version).name
        report['status'] = 'captured_not_reviewed'
        report['screenshot'] = image.name
    except Exception as exc:
        # Never publish GUI process output, environment dumps, or private paths.
        report['reason'] = type(exc).__name__
        print('Optional GUI capture unavailable: ' + type(exc).__name__)
        return 1
    finally:
        (output/'status.json').write_text(json.dumps(report, indent=2) + '\n')
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a') as summary:
            summary.write('Optional Linux GUI evidence: ' + report['status'] +
                          '. Visual review is required; this does not establish GUI acceptance.\n')

if __name__ == '__main__':
    sys.exit(main())
