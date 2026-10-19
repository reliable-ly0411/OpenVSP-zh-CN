#!/usr/bin/env python3
"""Build only the help targets and verify executable-relative resource paths.

The fixture needs CMake >= 3.24 and Ninja, but no compiler, OpenVSP libraries,
Pandoc, network access, or native OpenVSP executable.
"""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELP = ROOT / 'src/help'
CMAKE = shutil.which('cmake')
NINJA = shutil.which('ninja')


@unittest.skipUnless(CMAKE and NINJA, 'CMake and Ninja are required for help layout tests')
class HelpBuildLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run([CMAKE, '-E', 'capabilities'], check=True,
                                capture_output=True, text=True)
        cls.generators = {item['name'] for item in json.loads(result.stdout)['generators']}

    def run_cmake(self, *args):
        result = subprocess.run([CMAKE, *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def assert_resources(self, destination):
        expected = {Path('vsp_help'): HELP / 'vsp_help',
                    Path('github-pandoc.css'): HELP / 'github-pandoc.css'}
        expected.update({Path(path.name): path for path in (HELP / 'html').glob('*.html')})
        expected.update({Path('images') / path.relative_to(HELP / 'images'): path
                         for path in (HELP / 'images').rglob('*') if path.is_file()})
        self.assertGreater(len(expected), 2)
        for relative, source in expected.items():
            with self.subTest(resource=str(relative)):
                target = destination / relative
                self.assertTrue(target.is_file(), f'Missing help resource: {target}')
                self.assertEqual(target.read_bytes(), source.read_bytes())
        actual = {path.relative_to(destination) for path in destination.rglob('*') if path.is_file()}
        self.assertEqual(actual, set(expected))

    def check_layout(self, generator, configurations):
        if generator not in self.generators:
            self.skipTest(f'{generator} is unavailable')
        with tempfile.TemporaryDirectory(prefix='openvsp-help-layout-') as directory:
            fixture = Path(directory)
            # A stub rejects accidental regeneration even when Pandoc appears available.
            # Only the reviewed bundled HTML should be used by the default build.
            (fixture / 'pandocology.cmake').write_text(
                'set(PANDOC_EXECUTABLE "${CMAKE_COMMAND}")\n'
                'set(PANDOC_VERSION "99.0")\n'
                'function(ADD_DOCUMENT)\n'
                '  message(FATAL_ERROR "Unexpected regeneration of reviewed help")\n'
                'endfunction()\n', encoding='utf-8')
            help_path = HELP.as_posix().replace('"', '\\"')
            (fixture / 'CMakeLists.txt').write_text(
                'cmake_minimum_required(VERSION 3.24)\n'
                'project(HelpLayoutFixture LANGUAGES NONE)\n'
                'set(VSP_BINARY_DIR "${CMAKE_BINARY_DIR}")\n'
                # Deliberately wrong inherited values: the help directory must inspect
                # its generator itself and reset both multi- and single-config paths.
                'set(is_multi_config FALSE)\n'
                'set(conf_suffix "incorrect/")\n'
                'list(PREPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}")\n'
                f'add_subdirectory("{help_path}" help-build)\n', encoding='utf-8')
            build = fixture / 'build'
            self.run_cmake('-S', fixture, '-B', build, '-G', generator,
                           f'-DCMAKE_MAKE_PROGRAM={NINJA}')
            for configuration in configurations:
                config_args = ['--config', configuration] if configuration else []
                output = build / 'vsp'
                if configuration:
                    output /= configuration
                output /= 'help'
                # These independent targets must create their own parent directory.
                for target, source in [('copy_css', HELP / 'github-pandoc.css'),
                                       ('copy_help_marker', HELP / 'vsp_help'),
                                       ('copy_html_index', HELP / 'html/index.html')]:
                    if output.exists():
                        shutil.rmtree(output)
                    self.run_cmake('--build', build, *config_args, '--target', target,
                                   '--parallel', '4')
                    self.assertEqual((output / source.name).read_bytes(), source.read_bytes())
                shutil.rmtree(output)
                self.run_cmake('--build', build, *config_args, '--parallel', '8')
                self.assert_resources(output)
                # Installation stays at package-root/help, without configuration layers.
                install = fixture / ('install-' + (configuration or 'single'))
                self.run_cmake('--install', build, *config_args, '--prefix', install)
                self.assert_resources(install / 'help')

    def test_single_configuration_paths_and_install(self):
        self.check_layout('Ninja', [None])

    def test_multi_configuration_paths_and_install(self):
        self.check_layout('Ninja Multi-Config', ['Release', 'Debug'])


if __name__ == '__main__':
    unittest.main()
