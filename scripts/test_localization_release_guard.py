#!/usr/bin/env python3
"""Exercise candidate identity without mutating source or contacting a release service."""
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERSION_SOURCE = (ROOT / 'src/cmake/VSP_Version.cmake').read_text(encoding='utf-8')
VERSION = '.'.join(re.search(rf'SET\(\s*VSPVER_{key}\s+(\d+)\s*\)', VERSION_SOURCE)[1]
                   for key in ('MAJOR', 'MINOR', 'PATCH'))
ABOUT_SOURCE = (ROOT / 'src/gui_and_draw/MainVSPScreen.cpp').read_text(encoding='utf-8')
CANDIDATE = re.search(r'汉化版本：(\d+\.\d+\.\d+-zh-CN\.rc\.[1-9]\d*)\\n', ABOUT_SOURCE)[1]

class CandidateIdentityTests(unittest.TestCase):
    def run_guard(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/check_localization_release.py'), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def test_exact_candidate_passes(self):
        result = self.run_guard('--expected-tag', CANDIDATE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_version_report_matches_source(self):
        result = self.run_guard('--print-version')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), VERSION)

    def test_readme_current_identity_matches_candidate(self):
        readme = (ROOT / 'README_zh-CN.md').read_text(encoding='utf-8')
        self.assertIn('当前汉化版本：`' + CANDIDATE + '`', readme)

    def test_current_display_copy_is_tool_neutral(self):
        for name in ('src/gui_and_draw/MainVSPScreen.cpp', 'src/gui_and_draw/VSPChinese.cpp',
                     'src/help/index.md', 'src/help/html/index.html'):
            with self.subTest(source=name):
                self.assertNotIn('Codex', (ROOT / name).read_text(encoding='utf-8'))

    def test_other_version_is_rejected(self):
        self.assertNotEqual(self.run_guard('--expected-tag', '99.99.99-zh-CN.rc.1').returncode, 0)

    def test_other_revision_is_rejected(self):
        self.assertNotEqual(self.run_guard('--expected-tag', VERSION + '-zh-CN.rc.' + str(int(CANDIDATE.rsplit('.', 1)[1]) + 1)).returncode, 0)

    def test_current_source_cannot_impersonate_historical_release(self):
        self.assertNotEqual(self.run_guard('--expected-tag', VERSION + '-Codex-AI-zh-CN').returncode, 0)

    def test_zero_revision_is_rejected(self):
        self.assertNotEqual(self.run_guard('--expected-tag', VERSION + '-zh-CN.rc.0').returncode, 0)

if __name__ == '__main__':
    unittest.main()
