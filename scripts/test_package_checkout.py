#!/usr/bin/env python3
"""Verify Windows checkout handling without weakening model or binary comparisons."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


CHECKER = Path(__file__).with_name('check_localized_package.py')


class PackageCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        shutil.copyfile(CHECKER, self.root / 'scripts/check_localized_package.py')
        self.files = {name: b'text\nsecond line\n' for name in ('README.md', 'README_zh-CN.md', 'AGENTS.md', 'LICENSE')}
        self.files.update({
            '.gitattributes': b'* text=auto\n*.vsp3 -text\n',
            'vspIcon.png': b'\x89PNG\x00\r\n binary',
            'examples/model.vsp3': b'<model>\nkeep original bytes\n</model>\n',
            'examples/readme.txt': b'example\n',
            'src/help/html/index.html': b'<html>\nhelp\n</html>\n',
        })
        for name, data in self.files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Package test')
        self.git('config', 'user.email', 'package@example.invalid')
        self.git('add', '.')
        self.git('commit', '-m', 'source')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, check=True).stdout

    def archive(self, changed=None):
        changed = changed or {}
        archive = self.root / 'Windows.zip'
        with zipfile.ZipFile(archive, 'w') as z:
            for executable in ('vsp', 'vspscript', 'vspaero', 'vspviewer', 'vsploads'):
                z.writestr('OpenVSP/' + executable + '.exe', b'executable')
            for name in ('vsp_help', 'github-pandoc.css'):
                z.writestr('OpenVSP/help/' + name, b'resource')
            for name in self.files:
                if name == '.gitattributes':
                    continue
                data = changed.get(name, self.git('-c', 'core.autocrlf=true', '-c', 'core.eol=crlf', 'cat-file', '--filters', 'HEAD:' + name))
                target = name.replace('examples/', 'Official_Examples/').replace('src/help/html/', 'help/')
                z.writestr('OpenVSP/' + target, data)
        return archive

    def check(self, changed=None, windows=True):
        args = [sys.executable, str(self.root / 'scripts/check_localized_package.py')]
        if windows:
            args.append('--windows-checkout')
        args.append(str(self.archive(changed)))
        return subprocess.run(args, cwd=self.root, text=True, capture_output=True)

    def test_windows_text_checkout_is_accepted(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_default_comparison_stays_byte_exact(self):
        result = self.check(windows=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('README.md', result.stderr)

    def test_model_line_endings_are_not_normalized(self):
        result = self.check({'examples/model.vsp3': self.files['examples/model.vsp3'].replace(b'\n', b'\r\n')})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Packaged example differs', result.stderr)

    def test_binary_line_endings_are_not_normalized(self):
        result = self.check({'vspIcon.png': self.files['vspIcon.png'].replace(b'\r\n', b'\n')})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('vspIcon.png', result.stderr)


if __name__ == '__main__':
    unittest.main()
