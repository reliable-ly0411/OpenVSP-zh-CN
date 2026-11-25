#!/usr/bin/env python3
"""Require one coherent README marker, release heading, and About version."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_localization_release as guard


class LocalizedReleaseIdentityTests(unittest.TestCase):
    tag = '3.55.0-zh-CN.rc.2'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        files = {
            '.github/upstream.json': json.dumps({'version': '3.55.0', 'base_commit': 'a' * 40}),
            'README.md': '本仓库基于 OpenVSP 3.55.0，',
            'README_zh-CN.md': f'当前软件版本：OpenVSP 3.55.0\n当前汉化版本：`{self.tag}`\n'
                              f'## {self.tag}\nActual changes.\n',
            'AGENTS.md': '当前官方基线：OpenVSP 3.55.0，',
            'src/gui_and_draw/MainVSPScreen.cpp': 'VSPVERSION4\n'
                'https://github.com/reliable-ly0411/OpenVSP-zh-CN\n'
                f'汉化版本：{self.tag}\\n',
            'src/gui_and_draw/VSPChinese.cpp': 'VSPTranslate',
            'src/gui_and_draw/VSPChinese.h': '',
            'src/vsp/vsp.rc.in': '',
            'src/vsp/CMakeLists.txt': 'vsp.rc.in',
            'examples/Complete_Aircraft/identity_fixture.vsp3':
                '<Vsp_Geometry><Vehicle><Geom><ParmContainer><Name>Wing</Name>'
                '</ParmContainer></Geom></Vehicle></Vsp_Geometry>',
            'src/cmake/VSP_Version.cmake':
                'SET( VSPVER_MAJOR 3 )\nSET( VSPVER_MINOR 55 )\nSET( VSPVER_PATCH 0 )\n',
            'vspIcon.ico': '',
            'vspIcon.png': '',
        }
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def check(self, *extra):
        with patch.object(guard, 'ROOT', self.root), \
             patch.object(guard, 'VERSION_FILE', self.root / 'src/cmake/VSP_Version.cmake'), \
             patch.object(guard, 'RELEASE_NOTES_FILE', self.root / 'README_zh-CN.md'), \
             patch.object(guard, 'read_version', return_value='3.55.0'), \
             patch('sys.argv', ['check_localization_release.py', '--expected-tag', self.tag, *extra]), \
             contextlib.redirect_stdout(io.StringIO()):
            guard.main()

    def make_unbranded(self):
        (self.root / 'src/vsp/vsp.rc.in').unlink()
        (self.root / 'src/vsp/CMakeLists.txt').write_text('add_executable(vsp)')

    def test_explicit_ubuntu_accepts_unbranded_upstream_app(self):
        self.make_unbranded()
        self.check('--packaging-target', 'ubuntu-24.04-amd64')

    def test_windows_and_default_still_require_windows_resource(self):
        self.make_unbranded()
        for extra in [(), ('--packaging-target', 'windows')]:
            with self.subTest(extra=extra), self.assertRaisesRegex(SystemExit, 'vsp.rc.in'):
                self.check(*extra)

    def test_windows_still_checks_cmake_integration_even_with_resource(self):
        (self.root / 'src/vsp/CMakeLists.txt').write_text('add_executable(vsp)')
        with self.assertRaisesRegex(SystemExit, 'src/vsp/CMakeLists.txt'):
            self.check('--packaging-target', 'windows')

    def test_unsupported_platform_cannot_waive_checks(self):
        self.make_unbranded()
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            self.check('--packaging-target', 'ubuntu-arm')
        self.assertEqual(caught.exception.code, 2)

    def test_ubuntu_still_checks_assets_and_version(self):
        self.make_unbranded()
        asset = self.root / 'vspIcon.png'
        asset.unlink()
        with self.assertRaisesRegex(SystemExit, 'vspIcon.png'):
            self.check('--packaging-target', 'ubuntu-24.04-amd64')
        asset.touch()
        with self.assertRaisesRegex(SystemExit, '与源码版本'):
            self.check('--packaging-target', 'ubuntu-24.04-amd64',
                       '--expected-tag', '3.54.0-zh-CN.rc.2')

    def test_matching_marker_heading_and_about_are_accepted(self):
        self.check()

    def test_stale_readme_marker_is_rejected(self):
        path = self.root / 'README_zh-CN.md'
        path.write_text(path.read_text().replace(f'当前汉化版本：`{self.tag}`',
                                                '当前汉化版本：`3.55.0-zh-CN.rc.1`'))
        with self.assertRaisesRegex(SystemExit, '当前汉化版本'):
            self.check()

    def test_missing_release_heading_is_rejected(self):
        path = self.root / 'README_zh-CN.md'
        path.write_text(path.read_text().replace(f'## {self.tag}', '## 未发布'))
        with self.assertRaisesRegex(SystemExit, '发布更新说明缺失'):
            self.check()

    def test_stale_about_version_is_rejected(self):
        path = self.root / 'src/gui_and_draw/MainVSPScreen.cpp'
        path.write_text(path.read_text().replace(self.tag, '3.55.0-zh-CN.rc.1'))
        with self.assertRaisesRegex(SystemExit, 'MainVSPScreen.cpp'):
            self.check()


if __name__ == '__main__':
    unittest.main()
