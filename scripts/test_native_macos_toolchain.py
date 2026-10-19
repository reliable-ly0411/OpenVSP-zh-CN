"""Offline regression coverage; no macOS compiler or installer is executed."""
from copy import deepcopy
from pathlib import Path
import unittest

from backfill_plan import PLATFORMS as HISTORICAL
from native_plan import PLATFORMS
from native_macos_toolchain import bottle_contract, verify_install


class NativeMacToolchainTests(unittest.TestCase):
    def setUp(self):
        self.formula = dict(name='llvm@16', tap='homebrew/core', disabled=False,
                            versions={'stable': '16.0.6'}, revision=1,
                            bottle={'stable': {'files': {}}})
        for key in ('arm64_sonoma', 'sequoia'):
            self.formula['bottle']['stable']['files'][key] = dict(
                sha256='a' * 64, url='https://ghcr.io/v2/homebrew/core/llvm/16/blobs/sha256:' + 'a' * 64)

    def contract(self, **changes):
        args = dict(data={'formulae': [self.formula]}, target='macOS-14-arm64-Python3.11',
                    architecture='arm64', llvm='16', host_version='14.8.9')
        args.update(changes)
        return bottle_contract(**args)

    def compilers(self):
        return {name: dict(version='Homebrew clang version 16.0.6', architectures=['arm64'], sha256='b' * 64)
                for name in ('clang', 'clang++')}

    def test_native_arm_changes_without_rewriting_historical_matrix(self):
        self.assertEqual(next(p['llvm'] for p in PLATFORMS if p['runner'] == 'macos-14'), '16')
        self.assertEqual(next(p['llvm'] for p in HISTORICAL if p['runner'] == 'macos-14'), '18')

    def test_exact_arm_and_intel_bottles(self):
        self.assertEqual(self.contract()['bottle_tag'], 'arm64_sonoma')
        self.assertEqual(self.contract(target='macOS-15-x86_64-Python3.11', architecture='x86_64',
                                       host_version='15.7.1')['bottle_tag'], 'sequoia')

    def test_macos15_cannot_prove_macos14_runtime(self):
        with self.assertRaises(ValueError): self.contract(host_version='15.7.1')
        with self.assertRaises(ValueError): self.contract(architecture='x86_64')

    def test_absent_sonoma_bottle_never_falls_back_to_source(self):
        del self.formula['bottle']['stable']['files']['arm64_sonoma']
        with self.assertRaisesRegex(ValueError, 'source-build fallback'): self.contract()

    def test_unreviewed_llvm_and_untrusted_or_disabled_formula_rejected(self):
        with self.assertRaises(ValueError): self.contract(llvm='18')
        self.formula['tap'] = 'other/tap'
        with self.assertRaises(ValueError): self.contract()
        self.formula['tap'] = 'homebrew/core'; self.formula['disabled'] = True
        with self.assertRaises(ValueError): self.contract()

    def test_invalid_bottle_checksum_or_url_rejected(self):
        bottle = self.formula['bottle']['stable']['files']['arm64_sonoma']
        bottle['url'] = 'https://example.invalid/bottle'
        with self.assertRaises(ValueError): self.contract()
        bottle['sha256'] = 'bad'
        with self.assertRaises(ValueError): self.contract()

    def test_actual_bottled_compiler_identity_is_recorded(self):
        report = verify_install(self.contract(), {'poured_from_bottle': True, 'arch': 'arm64'},
                                '16.0.6_1', self.compilers())
        self.assertEqual(report['compilers']['clang++']['architectures'], ['arm64'])

    def test_wrong_keg_source_build_or_receipt_arch_rejected(self):
        for receipt, version in (({'poured_from_bottle': False}, '16.0.6_1'),
                                 ({'poured_from_bottle': True}, '16.0.6'),
                                 ({'poured_from_bottle': True, 'arch': 'x86_64'}, '16.0.6_1')):
            with self.subTest(receipt=receipt, version=version), self.assertRaises(ValueError):
                verify_install(self.contract(), receipt, version, self.compilers())

    def test_wrong_actual_compiler_arch_version_or_missing_compiler_rejected(self):
        for field, value in (('architectures', ['x86_64']), ('architectures', ['arm64', 'x86_64']),
                             ('version', 'Apple clang version 15.0.0'), ('sha256', 'invalid')):
            compilers = deepcopy(self.compilers()); compilers['clang++'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify_install(self.contract(), {'poured_from_bottle': True}, '16.0.6_1', compilers)
        with self.assertRaises(ValueError):
            verify_install(self.contract(), {'poured_from_bottle': True}, '16.0.6_1', {})

    def test_native_shell_gates_bottle_preflight_and_keeps_ci_evidence(self):
        script = Path(__file__).with_name('backfill_build.sh').read_text()
        self.assertIn('if [[ ${NATIVE_RELEASE:-false} == true ]]; then', script)
        self.assertIn('native_macos_toolchain.py" preflight', script)
        self.assertIn('--force-bottle', script)
        self.assertIn('native_macos_toolchain.py" verify', script)
        self.assertIn('"$ROOT/deliverables/toolchain.json"', script)


if __name__ == '__main__':
    unittest.main()
