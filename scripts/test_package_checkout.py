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
            'examples/CustomScripts/Cone.vsppart': b'void Init() {}\n',
            'examples/textures/test.png': b'\x89PNG\x00\r\ntexture',
            'examples/airfoil/test.af': b'0.0 1.0\n',
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
                if name.startswith(('examples/CustomScripts/', 'examples/textures/', 'examples/airfoil/')):
                    z.writestr('OpenVSP/' + name.removeprefix('examples/'), data)
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

    def test_missing_runtime_resource_fails_even_with_examples_copy(self):
        original = self.archive()
        stripped = self.root / 'missing-resources.zip'
        with zipfile.ZipFile(original) as source, zipfile.ZipFile(stripped, 'w') as target:
            for info in source.infolist():
                if '/CustomScripts/' in info.filename and '/Official_Examples/' not in info.filename:
                    continue
                target.writestr(info, source.read(info.filename))
        result = subprocess.run([sys.executable, str(self.root / 'scripts/check_localized_package.py'),
                                 '--windows-checkout', str(stripped)], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('runtime resource', result.stderr)


if __name__ == '__main__':
    unittest.main()
