"""Offline Windows build contracts; no installer or native executable is run."""
from pathlib import Path
import re
import unittest


class NativeWindowsBuildTests(unittest.TestCase):
    def setUp(self):
        self.script = Path(__file__).with_name('native_build_windows.ps1').read_text(encoding='utf-8')

    def test_only_required_swig_is_installed_and_failure_still_stops_build(self):
        installs = re.findall(r'^\s*(choco\s+install\b[^\r\n]*)', self.script, re.MULTILINE)
        self.assertEqual(installs, ['choco install --yes swig'])
        self.assertIn("choco install --yes swig\n"
                      "    if ($LASTEXITCODE -ne 0) { throw 'Build dependency installation failed' }",
                      self.script)

    def test_document_regeneration_stays_disabled(self):
        self.assertIn('-DVSP_NO_PYDOC=ON', self.script)
        self.assertIn('-DPANDOC_EXECUTABLE=O:/unavailable/pandoc', self.script)

    def test_source_and_package_verification_still_gate_success(self):
        for command, failure in (
                ('git diff --quiet --exit-code', 'Build modified tracked source'),
                ('git diff --cached --quiet --exit-code', 'Build modified index'),
                ('python -X utf8 O:\\tooling\\scripts\\native_verify.py O:\\stage O:\\source O:\\deliverables',
                 'Native package verification failed')):
            with self.subTest(command=command):
                self.assertIn(command + "\n    if ($LASTEXITCODE -ne 0) { throw '" + failure + "' }",
                              self.script)


if __name__ == '__main__':
    unittest.main()
