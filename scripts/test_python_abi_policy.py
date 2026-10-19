"""Offline checks for the packaged Python dependency/build ABI contract."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PythonAbiPolicyTests(unittest.TestCase):
    def test_requirement_and_conda_environment_pin_build_numpy(self):
        packages = ROOT / 'src/python_api/packages'
        self.assertIn('numpy==1.26.4', (packages / 'requirements.txt').read_text())
        self.assertIn('numpy=1.26.4', (packages / 'environment.yml.in').read_text())

    def test_each_package_numpy_requirement_has_abi_ceiling(self):
        packages = ROOT / 'src/python_api/packages'
        declarations = list(packages.glob('*/setup.py')) + [packages / 'openvsp/setup.py.in']
        for path in declarations:
            for requirement in re.findall(r'''["'](numpy[^"']*)["']''', path.read_text()):
                with self.subTest(package=path.parent.name):
                    self.assertEqual(requirement, 'numpy>=1.26.4,<2')

    def test_wrapper_declares_a_native_distribution(self):
        from types import ModuleType
        from unittest.mock import patch
        setup_calls = []
        package = ModuleType('setuptools')
        package.setup = lambda **kwargs: setup_calls.append(kwargs)
        dist = ModuleType('setuptools.dist')
        dist.Distribution = object
        source = (ROOT / 'src/python_api/packages/openvsp/setup.py.in').read_text()
        with patch.dict('sys.modules', {'setuptools': package, 'setuptools.dist': dist}):
            exec(compile(source, 'setup.py.in', 'exec'), {})
        self.assertEqual(len(setup_calls), 1)
        self.assertTrue(setup_calls[0]['distclass']().has_ext_modules())
        self.assertIn('numpy>=1.26.4,<2', setup_calls[0]['install_requires'])

    def test_manifest_includes_all_native_extension_suffixes(self):
        from fnmatch import fnmatchcase
        source = (ROOT / 'src/python_api/packages/openvsp/MANIFEST.in').read_text()
        patterns = re.findall(r'^include (.+)$', source, re.MULTILINE)
        for filename in ('_vsp.so', '_vsp.pyd', '_vsp.cpython-312-x86_64-linux-gnu.so',
                         '_vsp_g.so', '_vsp_g.pyd'):
            self.assertTrue(any(fnmatchcase('openvsp/' + filename, pattern) for pattern in patterns), filename)

    def test_manifest_preserves_bundled_runtime_closure(self):
        source = (ROOT / 'src/python_api/packages/openvsp/MANIFEST.in').read_text()
        for entry in ('graft openvsp/lib', 'graft openvsp/third-party-licenses',
                      'include openvsp/third-party-dependencies.json'):
            self.assertIn(entry, source)

    def test_conda_wrapper_runtime_matches_setup(self):
        source = (ROOT / 'src/python_api/packages/openvsp/conda-recipe/meta.yaml.in').read_text()
        runtime = source.split('  run:', 1)[1]
        requirements = set(re.findall(r'^    - (.+)$', runtime, re.MULTILINE))
        self.assertTrue({'python', 'numpy >=1.26.4,<2', 'degen_geom', 'utilities',
                         'openvsp_config'} <= requirements)

    def test_custom_smoke_covers_every_bundled_component(self):
        smoke = (ROOT / 'scripts/localization_resources_smoke.as').read_text()
        for source in (ROOT / 'examples/CustomScripts').glob('*.vsppart'):
            self.assertIn('"' + source.stem + '"', smoke)


if __name__ == '__main__':
    unittest.main()
