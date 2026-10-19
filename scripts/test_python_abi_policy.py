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

    def test_custom_smoke_covers_every_bundled_component(self):
        smoke = (ROOT / 'scripts/localization_resources_smoke.as').read_text()
        for source in (ROOT / 'examples/CustomScripts').glob('*.vsppart'):
            self.assertIn('"' + source.stem + '"', smoke)


if __name__ == '__main__':
    unittest.main()
