"""Exact new-rc archive names and unchanged historical naming contracts, offline."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import backfill_plan
import native_plan
import native_promote
import native_release
import native_verify
import release_asset_names
from backfill_verify import digest
from test_native_functional import functional_summary


# Independent literal expectations: five supported families, five targets each.
EXPECTED_NAMES = {
    '3.51.2': (
        'OpenVSP-3.51.2-Ubuntu-24.04_amd64-zh-CN.zip',
        'OpenVSP-3.51.2-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip',
        'OpenVSP-3.51.2-win64-Python3.11-zh-CN.zip',
        'OpenVSP-3.51.2-macos-14-ARM64-Python3.11-zh-CN.zip',
        'OpenVSP-3.51.2-macos-15-intel-X64-Python3.11-zh-CN.zip',
    ),
    '3.51.3': (
        'OpenVSP-3.51.3-Ubuntu-24.04_amd64-zh-CN.zip',
        'OpenVSP-3.51.3-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip',
        'OpenVSP-3.51.3-win64-Python3.11-zh-CN.zip',
        'OpenVSP-3.51.3-macos-14-ARM64-Python3.11-zh-CN.zip',
        'OpenVSP-3.51.3-macos-15-intel-X64-Python3.11-zh-CN.zip',
    ),
    '3.53.0': (
        'OpenVSP-3.53.0-Ubuntu-24.04_amd64-zh-CN.zip',
        'OpenVSP-3.53.0-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip',
        'OpenVSP-3.53.0-win64-Python3.11-zh-CN.zip',
        'OpenVSP-3.53.0-macos-14-ARM64-Python3.11-zh-CN.zip',
        'OpenVSP-3.53.0-macos-15-intel-X64-Python3.11-zh-CN.zip',
    ),
    '3.54.0': (
        'OpenVSP-3.54.0-Ubuntu-24.04_amd64-zh-CN.zip',
        'OpenVSP-3.54.0-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip',
        'OpenVSP-3.54.0-win64-Python3.11-zh-CN.zip',
        'OpenVSP-3.54.0-macos-14-ARM64-Python3.11-zh-CN.zip',
        'OpenVSP-3.54.0-macos-15-intel-X64-Python3.11-zh-CN.zip',
    ),
    '3.55.0': (
        'OpenVSP-3.55.0-Ubuntu-24.04_amd64-zh-CN.zip',
        'OpenVSP-3.55.0-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip',
        'OpenVSP-3.55.0-win64-Python3.11-zh-CN.zip',
        'OpenVSP-3.55.0-macos-14-ARM64-Python3.11-zh-CN.zip',
        'OpenVSP-3.55.0-macos-15-intel-X64-Python3.11-zh-CN.zip',
    ),
}
TARGETS = (
    dict(platform='Ubuntu-24.04_amd64', runner='ubuntu-24.04', arch='x86_64', python='3.12', llvm=''),
    dict(platform='Ubuntu-24.04_arm64-Python3.12', runner='ubuntu-24.04-arm', arch='aarch64', python='3.12', llvm=''),
    dict(platform='win64', runner='windows-2022', arch='x86_64', python='3.11', llvm=''),
    dict(platform='macOS-14-arm64-Python3.11', runner='macos-14', arch='arm64', python='3.11', llvm='16'),
    dict(platform='macOS-15-x86_64-Python3.11', runner='macos-15-intel', arch='x86_64', python='3.11', llvm='16'),
)
SOURCE, WORKFLOW, RUN = 'a' * 40, 'b' * 40, '123'


class NativeAssetNameTests(unittest.TestCase):
    def test_all_twenty_five_names_match_literal_expectations(self):
        self.assertEqual(set(EXPECTED_NAMES), {v for v, _, _ in backfill_plan.RELEASES})
        for version, names in EXPECTED_NAMES.items():
            with self.subTest(version=version):
                self.assertEqual(tuple(native_plan.asset_name(version, p['platform']) for p in TARGETS), names)

    def test_mapping_covers_only_native_ids_and_all_names_are_unique(self):
        self.assertEqual(set(native_plan.ARCHIVE_PLATFORMS), {p['platform'] for p in TARGETS})
        names = [native_plan.asset_name(v, p['platform']) for v in EXPECTED_NAMES for p in TARGETS]
        self.assertEqual(len(names), 25)
        self.assertEqual(len(set(names)), 25)
        for name in names:
            self.assertEqual(Path(name).name, name)
            self.assertTrue(name.endswith('-zh-CN.zip'))

    def test_build_ids_runners_architectures_abis_and_llvm_do_not_change(self):
        self.assertEqual(native_plan.PLATFORMS, TARGETS)
        for version in EXPECTED_NAMES:
            tag = version + '-zh-CN.rc.1'
            self.assertEqual(native_plan.matrix(SOURCE, tag)['include'],
                             [dict(version=version, tag=tag, sha=SOURCE, **p) for p in TARGETS])

    def test_windows_name_always_records_the_actual_python_abi(self):
        target = next(p for p in native_plan.PLATFORMS if p['platform'] == 'win64')
        for version in EXPECTED_NAMES:
            name = native_plan.asset_name(version, 'win64')
            self.assertEqual(name, f'OpenVSP-{version}-win64-Python3.11-zh-CN.zip')
            self.assertIn('-Python' + target['python'] + '-', name)

    def test_unknown_versions_platforms_and_public_spelling_aliases_are_rejected(self):
        for platform in ('win64-Python3.11', 'macos-14-ARM64-Python3.11',
                         'macos-15-intel-X64-Python3.11', '../win64', 'Windows-x64', None):
            with self.subTest(platform=platform), self.assertRaises(ValueError):
                native_plan.asset_name('3.55.0', platform)
        for version in ('3.56.0', '3.55.0-zh-CN.rc.1', '../3.55.0', None):
            with self.subTest(version=version), self.assertRaises(ValueError):
                native_plan.asset_name(version, 'win64')

    def test_packager_release_and_promotion_share_the_only_naming_function(self):
        for module in (native_verify, native_release, native_promote):
            self.assertIs(module.asset_name, native_plan.asset_name)

    def test_historical_dual_platform_names_and_candidates_are_unchanged(self):
        for version, tag, _ in backfill_plan.RELEASES:
            for platform, suffix in (('Ubuntu-24.04-x86_64', 'Ubuntu-24.04_amd64'),
                                     ('Windows-x64', 'win64')):
                with self.subTest(tag=tag, platform=platform):
                    name = f'OpenVSP-{version}-{suffix}-zh-CN.zip'
                    self.assertEqual(release_asset_names.asset_name(tag, platform), name)
                    self.assertEqual(release_asset_names.asset_candidates(tag, platform),
                                     (name, f'OpenVSP-{tag}-{platform}.zip'))

    def test_historical_backfill_platforms_and_archive_expression_are_unchanged(self):
        self.assertEqual(tuple(p['platform'] for p in backfill_plan.PLATFORMS), (
            'macOS-14-arm64-Python3.11', 'macOS-15-x86_64-Python3.11', 'Ubuntu-24.04_arm64-Python3.12'))
        script = Path(__file__).with_name('backfill_verify.py').read_text(encoding='utf-8')
        # Backfill deliberately keeps its historical formatter, independent of native_plan.
        self.assertIn('name = f"OpenVSP-{os.environ[\'BACKFILL_VERSION\']}-{os.environ[\'BACKFILL_PLATFORM\']}-zh-CN.zip"', script)
        self.assertNotIn('from native_plan import', script)
        self.assertEqual(len(backfill_plan.matrix('all')['include']), 15)


class NativeAssetGateTests(unittest.TestCase):
    def fixture(self, root, version):
        tag = version + '-zh-CN.rc.1'
        artifacts, output = root / 'artifacts', root / 'public'
        reports = []
        for target, name in zip(TARGETS, EXPECTED_NAMES[version]):
            folder = artifacts / target['platform']; folder.mkdir(parents=True)
            package = folder / name
            with zipfile.ZipFile(package, 'w') as z:
                z.writestr('OpenVSP/fixture.txt', 'Inert fixture for ' + target['platform'])
            report = dict(schema=2, tag=tag, source_sha=SOURCE, version=version,
                          platform=target['platform'], architecture=target['arch'], python=target['python'],
                          workflow_sha=WORKFLOW, run_id=RUN, archive=name, bytes=package.stat().st_size,
                          sha256=digest(package), source_tracked_files_clean=True,
                          checks=sorted(native_plan.REQUIRED_CHECKS), requirements_install={'numpy': '1.26.4'},
                          functional_smoke=functional_summary())
            reports.append(report)
            (folder / 'verification.json').write_text(json.dumps(report), encoding='utf-8')
        return tag, artifacts, output, reports

    def test_all_families_assemble_extract_validate_reports_manifest_and_gui_hash(self):
        for version, names in EXPECTED_NAMES.items():
            with self.subTest(version=version), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                tag, artifacts, output, reports = self.fixture(root, version)
                native_release.prepare_assets(artifacts, output, SOURCE, tag, RUN, WORKFLOW)
                expected = set(names) | {'SHA256SUMS.txt'}
                self.assertEqual({p.name for p in output.iterdir()}, expected)
                self.assertEqual(set(native_release.verify_manifest(output, version)), set(names))
                evidence = dict(schema=1, source_sha=SOURCE, tag=tag, run_id=RUN, workflow_sha=WORKFLOW,
                                manifest_sha256=digest(output / 'SHA256SUMS.txt'), reports=reports)
                archive, extracted = root / 'artifact.zip', root / 'extracted'
                with zipfile.ZipFile(archive, 'w') as z:
                    for path in output.iterdir():
                        z.write(path, path.name)
                native_promote.extract_artifact(archive, extracted, expected)
                native_promote.validate_evidence(evidence, extracted, SOURCE, tag, RUN, WORKFLOW)
                review = dict(manifest_sha256=evidence['manifest_sha256'],
                              linux_gui_sha256=digest(extracted / names[0]), validation_note='Inert test fixture')
                native_release.validate_gui_review(extracted, version, review)
                with self.assertRaises(ValueError):
                    native_release.validate_gui_review(extracted, version, dict(review, linux_gui_sha256=digest(extracted / names[2])))

    def test_old_windows_and_mac_report_names_are_rejected_without_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            tag, artifacts, output, reports = self.fixture(Path(temp), '3.55.0')
            native_release.prepare_assets(artifacts, output, SOURCE, tag, RUN, WORKFLOW)
            evidence = dict(schema=1, source_sha=SOURCE, tag=tag, run_id=RUN, workflow_sha=WORKFLOW,
                            manifest_sha256=digest(output / 'SHA256SUMS.txt'), reports=reports)
            for index in (2, 3, 4):
                bad = copy.deepcopy(evidence)
                bad['reports'][index]['archive'] = f'OpenVSP-3.55.0-{TARGETS[index]["platform"]}-zh-CN.zip'
                with self.subTest(platform=TARGETS[index]['platform']), self.assertRaises(ValueError):
                    native_promote.validate_evidence(bad, output, SOURCE, tag, RUN, WORKFLOW)

    def test_old_archive_names_block_assembly_before_staging(self):
        for index in (2, 3, 4):
            with self.subTest(platform=TARGETS[index]['platform']), tempfile.TemporaryDirectory() as temp:
                tag, artifacts, output, reports = self.fixture(Path(temp), '3.55.0')
                folder = artifacts / TARGETS[index]['platform']
                old = f'OpenVSP-3.55.0-{TARGETS[index]["platform"]}-zh-CN.zip'
                (folder / EXPECTED_NAMES['3.55.0'][index]).rename(folder / old)
                reports[index]['archive'] = old
                (folder / 'verification.json').write_text(json.dumps(reports[index]), encoding='utf-8')
                with self.assertRaises(ValueError):
                    native_release.prepare_assets(artifacts, output, SOURCE, tag, RUN, WORKFLOW)
                self.assertFalse(output.exists())

    def test_old_archive_names_and_matching_checksums_are_rejected(self):
        for index in (2, 3, 4):
            with self.subTest(platform=TARGETS[index]['platform']), tempfile.TemporaryDirectory() as temp:
                tag, artifacts, output, _ = self.fixture(Path(temp), '3.55.0')
                native_release.prepare_assets(artifacts, output, SOURCE, tag, RUN, WORKFLOW)
                old = f'OpenVSP-3.55.0-{TARGETS[index]["platform"]}-zh-CN.zip'
                new = EXPECTED_NAMES['3.55.0'][index]
                (output / new).rename(output / old)
                manifest = output / 'SHA256SUMS.txt'
                manifest.write_text(manifest.read_text().replace(new, old))
                with self.assertRaises(ValueError):
                    native_release.verify_manifest(output, '3.55.0')
                artifact = Path(temp) / 'old-names.zip'
                with zipfile.ZipFile(artifact, 'w') as z:
                    for path in output.iterdir():
                        z.write(path, path.name)
                with self.assertRaises(ValueError):
                    native_promote.extract_artifact(artifact, Path(temp) / 'extracted',
                                                   set(EXPECTED_NAMES['3.55.0']) | {'SHA256SUMS.txt'})
                self.assertEqual(list((Path(temp) / 'extracted').iterdir()), [])


if __name__ == '__main__':
    unittest.main()
