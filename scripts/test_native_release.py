"""Offline native release gates: no network, binaries, tags or release mutation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from backfill_verify import digest
from native_plan import PLATFORMS, REQUIRED_CHECKS, asset_name, matrix, validate_inputs
from native_release import find_release, prepare_assets, publish as publish_original, verify_manifest, release_body
from test_native_functional import functional_summary

SOURCE = 'a' * 40
WORKFLOW = 'b' * 40
TAG = '3.55.0-zh-CN.rc.1'


def review_for(directory):
    return dict(manifest_sha256=digest(directory / 'SHA256SUMS.txt'),
                linux_gui_sha256=digest(directory / asset_name('3.55.0', 'Ubuntu-24.04_amd64')),
                validation_note='Reviewed the exact Linux package: main, wing, name/path roundtrip.')


def publish(client, directory, source_sha, tag):
    return publish_original(client, directory, source_sha, tag, review=review_for(directory))


class FakeGitHub:
    repository = 'example/repo'

    def __init__(self):
        self.ref = None
        self.release = None
        self.data = {}
        self.writes = []
        self.fail_upload = None
        self.corrupt_download = False

    def api(self, path, method='GET', data=None, missing=False):
        if method != 'GET':
            self.writes.append((path, method, copy.deepcopy(data)))
        if path.startswith('releases?'):
            return [copy.deepcopy(self.release)] if self.release else []
        if path.startswith('git/ref/tags/'):
            return copy.deepcopy(self.ref)
        if path == 'git/refs' and method == 'POST':
            if self.ref:
                raise ValueError('Tag collision')
            self.ref = {'object': {'type': 'commit', 'sha': data['sha']}}
            return copy.deepcopy(self.ref)
        if path == 'releases' and method == 'POST':
            self.release = dict(data, id=1, assets=[], upload_url='https://uploads.github.com/repos/example/repo/releases/1/assets{?name}', html_url='https://github.com/example/repo/releases/tag/' + TAG)
            return copy.deepcopy(self.release)
        if path == 'releases/1':
            if method == 'PATCH':
                self.release.update(data)
            return copy.deepcopy(self.release)
        raise AssertionError((path, method))

    def upload(self, release, path):
        self.writes.append(('upload', path.name))
        identifier = len(self.data) + 1
        self.data[identifier] = path.read_bytes()
        self.release['assets'].append({'id': identifier, 'name': path.name})
        if self.fail_upload == len(self.data):
            raise RuntimeError('Simulated transport failure after accepted upload')

    def download(self, asset, path):
        path.write_bytes(self.data[asset['id']] + (b'corrupt' if self.corrupt_download else b''))


class NativePlanTests(unittest.TestCase):
    def test_exact_five_targets_and_supported_families(self):
        for version in ('3.51.2', '3.51.3', '3.53.0', '3.54.0', '3.55.0'):
            jobs = matrix(SOURCE, version + '-zh-CN.rc.1')['include']
            self.assertEqual(len(jobs), 5)
            self.assertEqual({j['runner'] for j in jobs}, {'ubuntu-24.04', 'ubuntu-24.04-arm', 'windows-2022', 'macos-14', 'macos-15-intel'})
            self.assertEqual({j['sha'] for j in jobs}, {SOURCE})
            self.assertEqual({j['python'] for j in jobs if j['runner'].startswith('ubuntu')}, {'3.12'})

    def test_old_tags_dev_snapshots_and_shell_input_rejected(self):
        for tag in ('3.55.0-Codex-AI-zh-CN', '3.55.0-zh-CN.rc.0', '3.55.0-zh-CN.rc.01',
                    '3.56.0-zh-CN.rc.1', '3.55.0-zh-CN.dev.aaaaaaaaaaaa', TAG + '; echo injected'):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                validate_inputs(SOURCE, tag)
        for source in ('main', 'a' * 39, 'A' * 40, SOURCE + '\n'):
            with self.assertRaises(ValueError):
                validate_inputs(source, TAG)

    def test_new_release_text_contains_no_ai_marketing(self):
        body = release_body(TAG, SOURCE, 'example/repo')
        self.assertNotIn('Codex', body)
        self.assertNotIn('OpenAI', body)
        self.assertIn('待目视', body)

    def test_rc3_names_are_revision_scoped(self):
        for version in ('3.51.2', '3.51.3', '3.53.0', '3.54.0', '3.55.0'):
            for revision in (1, 2, 3):
                body = release_body(f'{version}-zh-CN.rc.{revision}', SOURCE, 'example/repo')
                self.assertEqual('rc.3 新增：' in body, revision >= 3)
                if revision >= 3:
                    self.assertIn('Adjust', body)
                    self.assertIn('固定界面标题仍正常汉化', body)
                    self.assertIn('不修改模型数据、参数 ID 或接口', body)


class NativeReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.artifacts = self.root / 'artifacts'; self.artifacts.mkdir()
        self.output = self.root / 'public'
        for target in PLATFORMS:
            folder = self.artifacts / target['platform']; folder.mkdir()
            name = asset_name('3.55.0', target['platform'])
            package = folder / name
            with zipfile.ZipFile(package, 'w') as z:
                z.writestr('OpenVSP/fixture.txt', 'Inert package fixture')
            report = dict(schema=2, tag=TAG, source_sha=SOURCE, version='3.55.0',
                          platform=target['platform'], architecture=target['arch'], python=target['python'],
                          workflow_sha=WORKFLOW, run_id='123', archive=name, bytes=package.stat().st_size,
                          sha256=digest(package), source_tracked_files_clean=True,
                          checks=sorted(REQUIRED_CHECKS), requirements_install={'numpy': '1.26.4'},
                          functional_smoke=functional_summary())
            (folder / 'verification.json').write_text(json.dumps(report))

    def prepare(self):
        return prepare_assets(self.artifacts, self.output, SOURCE, TAG, '123', WORKFLOW)

    def test_five_zip_manifest_uses_final_names_and_excludes_ci_reports(self):
        self.prepare()
        self.assertEqual(len(list(self.output.iterdir())), 6)
        self.assertNotIn('verification.json', {p.name for p in self.output.iterdir()})
        self.assertEqual(len(verify_manifest(self.output, '3.55.0')), 5)
        self.assertNotIn('Codex', (self.output / 'SHA256SUMS.txt').read_text())

    def test_wrong_source_run_or_missing_checks_block_assembly(self):
        report_file = next(self.artifacts.rglob('verification.json'))
        original = json.loads(report_file.read_text())
        for key, value in [('source_sha', 'c'*40), ('run_id', '124'), ('checks', []),
                           ('workflow_sha', 'd'*40), ('source_tracked_files_clean', False),
                           ('requirements_install', {'numpy': '2.0'})]:
            with self.subTest(key=key):
                report_file.write_text(json.dumps(dict(original, **{key:value})))
                with self.assertRaises(ValueError):
                    self.prepare()
                self.assertFalse(self.output.exists())
        report_file.write_text(json.dumps(original))

    def test_missing_export_analysis_checks_or_functional_evidence_block_assembly(self):
        path = next(self.artifacts.rglob('verification.json'))
        original = json.loads(path.read_text())
        for check in ('Unicode STL export and triangle validation', 'CompGeom and VSPAERO CLI analysis'):
            changed = copy.deepcopy(original); changed['checks'].remove(check)
            path.write_text(json.dumps(changed))
            with self.subTest(check=check), self.assertRaisesRegex(ValueError, 'Required native checks'):
                self.prepare()
        changed = copy.deepcopy(original); del changed['functional_smoke']
        invalid = [changed, dict(original, functional_smoke={})]
        changed = copy.deepcopy(original); changed['functional_smoke']['vspaero_api']['final_lift_nonzero'] = False
        invalid.append(changed)
        changed = copy.deepcopy(original); del changed['functional_smoke']['vspaero_cli']; invalid.append(changed)
        changed = copy.deepcopy(original); changed['functional_smoke']['vspaero_cli']['exit_code'] = 1; invalid.append(changed)
        for report in invalid:
            path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, 'export/analysis evidence'): self.prepare()
            self.assertFalse(self.output.exists())

    def test_missing_platform_corrupt_zip_extra_zip_and_ambiguous_reports_fail(self):
        report = next(self.artifacts.rglob('verification.json'))
        backup = report.read_bytes(); report.unlink()
        with self.assertRaises(ValueError): self.prepare()
        report.write_bytes(backup)
        extra = self.artifacts / 'unexpected.zip'; extra.write_bytes(b'extra')
        with self.assertRaises(ValueError): self.prepare()
        extra.unlink()
        package = next(self.artifacts.rglob('*.zip')); package.write_bytes(b'changed')
        with self.assertRaises(ValueError): self.prepare()

    def test_wrong_or_duplicate_manifest_name_is_rejected(self):
        self.prepare()
        path = self.output / 'SHA256SUMS.txt'
        original = path.read_text()
        for bad in (original.replace('Ubuntu-24.04_amd64', 'old-name'), original + original.splitlines()[0] + '\n',
                    original.replace('  OpenVSP-', '  ../OpenVSP-', 1)):
            path.write_text(bad)
            with self.assertRaises(ValueError): verify_manifest(self.output, '3.55.0')
        path.write_text(original)

    def test_existing_public_release_and_moved_tag_are_never_changed(self):
        self.prepare()
        for public in (True, False):
            client = FakeGitHub()
            if public:
                client.release = {'tag_name': TAG, 'draft': False, 'prerelease': True}
            else:
                client.ref = {'object': {'type': 'commit', 'sha': 'c'*40}}
            with self.assertRaises(ValueError): publish(client, self.output, SOURCE, TAG)
            self.assertEqual(client.writes, [])

    def test_success_is_add_only_and_final_publish_happens_after_readback(self):
        self.prepare(); client = FakeGitHub()
        result = publish(client, self.output, SOURCE, TAG)
        self.assertFalse(result['draft'])
        self.assertTrue(result['prerelease'])
        self.assertEqual(result['make_latest'], 'false')
        self.assertEqual(len(client.data), 6)
        self.assertEqual(client.writes[-1][0:2], ('releases/1', 'PATCH'))
        self.assertFalse(any(write[1] == 'DELETE' for write in client.writes))
        self.assertEqual([write[0] for write in client.writes if write[1] == 'PATCH'], ['releases/1'])

    def test_interrupted_draft_resumes_without_reuploading_existing_assets(self):
        self.prepare(); client = FakeGitHub(); client.fail_upload = 2
        with self.assertRaises(RuntimeError): publish(client, self.output, SOURCE, TAG)
        self.assertTrue(client.release['draft'])
        self.assertEqual(len(client.data), 2)
        before = [write for write in client.writes if write[0] == 'upload']
        client.fail_upload = None
        publish(client, self.output, SOURCE, TAG)
        uploads = [write for write in client.writes if write[0] == 'upload']
        self.assertEqual(len(uploads), 6)
        self.assertEqual(uploads[:2], before)
        self.assertEqual(len([w for w in client.writes if w[:2] == ('git/refs', 'POST')]), 1)

    def test_missing_or_wrong_gui_acceptance_blocks_all_writes(self):
        self.prepare(); client = FakeGitHub()
        for review in (None, dict(review_for(self.output), linux_gui_sha256='c'*64)):
            with self.assertRaises(ValueError):
                publish_original(client, self.output, SOURCE, TAG, review=review)
            self.assertEqual(client.writes, [])

    def test_corrupt_remote_readback_never_publicizes(self):
        self.prepare(); client = FakeGitHub(); client.corrupt_download = True
        with self.assertRaises(ValueError): publish(client, self.output, SOURCE, TAG)
        self.assertTrue(client.release['draft'])
        self.assertFalse(any(w[1] == 'PATCH' for w in client.writes))

    def test_existing_draft_with_different_bytes_is_not_replaced(self):
        self.prepare(); client = FakeGitHub(); client.fail_upload = 1
        with self.assertRaises(RuntimeError): publish(client, self.output, SOURCE, TAG)
        client.data[1] = b'different build bytes'
        before = list(client.writes)
        with self.assertRaises(ValueError): publish(client, self.output, SOURCE, TAG)
        self.assertEqual(client.writes, before)

    def test_pagination_detects_duplicates_across_pages(self):
        release = {'tag_name': TAG, 'draft': True}
        with patch('builtins.print'), patch.object(FakeGitHub, 'api') as api:
            api.side_effect = [[{'tag_name': 'other'}] * 99 + [release], [release]]
            with self.assertRaises(ValueError): find_release(api, TAG)
            self.assertIn('page=2', api.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
