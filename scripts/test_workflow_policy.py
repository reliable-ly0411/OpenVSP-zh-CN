"""Keep credential boundaries and opt-in maintenance explicit in workflow text."""
from pathlib import Path
import copy
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import native_plan
import native_promote
import test_native_release as release_fixtures

ROOT = Path(__file__).resolve().parents[1]


class WorkflowPolicyTests(unittest.TestCase):
    def test_every_external_action_uses_full_commit_sha(self):
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            for action in re.findall(r'\buses:\s*([^\s#]+)', path.read_text()):
                if not action.startswith('./'):
                    with self.subTest(path=path.name, action=action):
                        self.assertRegex(action, r'^[\w./-]+@[0-9a-f]{40}$')

    def test_legacy_build_is_explicitly_read_only(self):
        text = (ROOT / '.github/workflows/build.yml').read_text()
        self.assertIn('\npermissions:\n  contents: read\n', text)
        self.assertIn('persist-credentials: false', text)

    def test_merged_tree_cannot_supply_privileged_maintenance_code(self):
        text = (ROOT / '.github/workflows/prepare-upstream-update.yml').read_text()
        self.assertIn('persist-credentials: false', text)
        self.assertLess(text.index('Snapshot trusted maintenance tools'), text.index('Prepare upstream merge'))
        self.assertIn('python3 -I "$RUNNER_TEMP/openvsp-maintenance/check_localization_release.py" --source "$GITHUB_WORKSPACE"', text)
        self.assertNotIn('python3 scripts/', text)
        self.assertEqual(text.count('PUSH_TOKEN:'), 1)
        self.assertLess(text.index('Check and commit candidate without write credentials'), text.index('PUSH_TOKEN:'))
        self.assertIn('GIT_CONFIG_KEY_1=core.hooksPath', text)
        self.assertNotIn('refs/heads/main', text)

    def test_notification_and_cleanup_are_opt_in_and_separate(self):
        text = (ROOT / '.github/workflows/upstream-watch.yml').read_text()
        self.assertIn("vars.OPENVSP_NOTIFY_UPSTREAM_FAILURES == 'true'", text)
        self.assertIn("vars.OPENVSP_CLEAN_MERGED_CANDIDATES == 'true'", text)
        self.assertIn('cleanup --output candidate-retention-plan.json', text)
        self.assertIn('notify --apply', text)
        self.assertIn('cleanup --apply --output candidate-cleanup-record.json', text)
        self.assertIn('retention-days: 90', text)
        self.assertNotIn('native-promote', text)

    def test_backfill_checks_untracked_source_and_builds_tests_outside_source(self):
        text = (ROOT / 'scripts/backfill_build.sh').read_text()
        self.assertIn('python "$TOOLS/check_source_worktree.py" "$SOURCE"', text)
        self.assertIn('-B "$ROOT/localization-tests"', text)
        self.assertNotIn('-B localization-tests\n', text)
        native = (ROOT / 'scripts/native_verify.py').read_text()
        self.assertIn('worktree_clean = require_clean_source(source)', native)
        self.assertIn('source_worktree_clean=worktree_clean', native)

    def test_native_publication_serializes_all_tags_without_changing_build_lock(self):
        promote = (ROOT / '.github/workflows/native-promote.yml').read_text()
        build = (ROOT / '.github/workflows/native-prerelease.yml').read_text()
        self.assertIn('concurrency:\n  group: native-prerelease-${{ inputs.new_tag }}\n'
                      '  cancel-in-progress: false\n', promote)
        self.assertIn('    concurrency:\n      group: openvsp-native-release-publication\n'
                      '      queue: max\n      cancel-in-progress: false\n', promote)
        self.assertIn("group: native-prerelease-${{ inputs.new_tag || github.ref }}", build)
        self.assertNotIn('openvsp-native-release-publication', build)


class NativeFamilyPlanTests(unittest.TestCase):
    """Exercise ancestry against actual temporary Git graphs, without any network."""
    version = '3.51.2'

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.source = Path(temp.name)
        self.git('init', '--quiet')
        self.git('config', 'user.name', 'Offline test')
        self.git('config', 'user.email', 'test@example.invalid')
        path = self.source / 'src/cmake/VSP_Version.cmake'
        path.parent.mkdir(parents=True)
        path.write_text('SET(VSPVER_MAJOR 3)\nSET(VSPVER_MINOR 51)\nSET(VSPVER_PATCH 2)\n')
        self.git('add', '.')
        self.baseline = self.commit('Historical family baseline')
        self.previous = self.commit('Previous family revision')
        self.head = self.commit('Next family revision')
        self.patcher = patch.object(native_plan, 'RELEASES', ((self.version, 'historical', self.baseline),))
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.source), *args], text=True,
                                       stderr=subprocess.PIPE).strip()

    def commit(self, message):
        self.git('commit', '--quiet', '--allow-empty', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def tag(self, revision):
        return f'{self.version}-zh-CN.rc.{revision}'

    def validate(self, revision, source=None):
        return native_plan.validate_source(self.source, source or self.head, self.tag(revision))

    def test_first_rc_and_descendant_need_only_their_own_family(self):
        self.assertEqual(self.validate(1), self.version)
        self.git('tag', self.tag(2), self.previous)
        self.git('tag', '3.55.0-zh-CN.rc.999', self.head)
        self.git('tag', '3.54.0-zh-CN.rc.malformed', self.head)
        # An unrelated current-main tip is intentionally NOT an ancestor.
        self.git('checkout', '--quiet', '--detach', self.baseline)
        main_tip = self.commit('Independent current main work')
        self.git('branch', 'current-main', main_tip)
        self.git('checkout', '--quiet', '--detach', self.head)
        self.assertEqual(self.validate(3), self.version)

    def test_numeric_revision_order_and_rollback(self):
        self.git('tag', self.tag(2), self.previous)
        self.git('tag', self.tag(10), self.head)
        for revision in (1, 3, 9):
            with self.subTest(revision=revision), self.assertRaisesRegex(ValueError, 'increment'):
                self.validate(revision)
        self.assertEqual(self.validate(11), self.version)

    def test_annotated_predecessor_is_resolved_to_commit(self):
        self.git('tag', '-a', self.tag(2), self.previous, '-m', 'Offline annotated predecessor')
        self.assertEqual(self.validate(3), self.version)

    def test_behind_and_diverged_sources_cannot_use_the_old_baseline(self):
        self.git('tag', self.tag(2), self.previous)
        self.git('checkout', '--quiet', '--detach', self.baseline)
        with self.assertRaises(subprocess.CalledProcessError):
            self.validate(3, self.baseline)
        diverged = self.commit('Sibling branch lacking the published revision')
        with self.assertRaises(subprocess.CalledProcessError):
            self.validate(3, diverged)

    def test_target_same_sha_recovery_still_checks_previous_ancestry(self):
        self.git('tag', self.tag(2), self.previous)
        self.git('tag', self.tag(3), self.head)
        self.assertEqual(self.validate(3), self.version)
        self.git('checkout', '--quiet', '--detach', self.baseline)
        with self.assertRaisesRegex(ValueError, 'exact source'):
            self.validate(3, self.baseline)
        sibling = self.commit('Interrupted draft from an invalid sibling')
        self.git('tag', self.tag(4), sibling)
        with self.assertRaises(subprocess.CalledProcessError):
            self.validate(4, sibling)

    def test_same_sha_target_does_not_bypass_a_later_revision(self):
        self.git('tag', self.tag(1), self.head)
        self.git('tag', self.tag(2), self.head)
        with self.assertRaisesRegex(ValueError, 'increment'):
            self.validate(1)

    def test_malformed_family_rc_tags_fail_closed(self):
        for revision in ('0', '01', '2suffix', '2.1', '2\N{ARABIC-INDIC DIGIT ONE}'):
            with self.subTest(revision=revision):
                self.git('tag', self.tag(revision), self.previous)
                with self.assertRaisesRegex(ValueError, 'Malformed'):
                    self.validate(3)
                self.git('tag', '-d', self.tag(revision))

    def test_shallow_history_is_rejected(self):
        real_check_output = subprocess.check_output
        def shallow(command, **kwargs):
            if command[-1] == '--is-shallow-repository':
                return 'true\n'
            return real_check_output(command, **kwargs)
        with patch.object(native_plan.subprocess, 'check_output', side_effect=shallow):
            with self.assertRaisesRegex(ValueError, 'full-history'):
                self.validate(1)


class FamilyGitHubFixture(release_fixtures.FakeGitHub):
    """In-memory Release catalog plus the existing add-only publication fixture."""
    def __init__(self):
        super().__init__()
        self.catalog = []
        self.calls = []
        self.comparisons = {}
        self.latest_sha = 'b' * 40
        self.on_download = None

    def api(self, path, method='GET', data=None, missing=False):
        self.calls.append((path, method))
        if method == 'GET' and path.startswith('releases?'):
            page = int(re.search(r'[?&]page=([0-9]+)', path)[1])
            rows = self.catalog + ([self.release] if self.release else [])
            return copy.deepcopy(rows[(page - 1) * 100:page * 100])
        if method == 'GET' and path.startswith('commits/'):
            return {'sha': self.latest_sha}
        if method == 'GET' and path.startswith('compare/'):
            ancestor, source = re.fullmatch(r'compare/([0-9a-f]{40})\.\.\.([0-9a-f]{40})\?per_page=1', path).groups()
            if ancestor in self.comparisons:
                return copy.deepcopy(self.comparisons[ancestor])
            same = ancestor == source
            return dict(status='identical' if same else 'ahead', ahead_by=0 if same else 1,
                        behind_by=0, base_commit={'sha': ancestor}, merge_base_commit={'sha': ancestor})
        return super().api(path, method, data, missing)

    def download(self, asset, path):
        super().download(asset, path)
        if self.on_download:
            self.on_download(self)


class NativeFamilyPromotionTests(unittest.TestCase):
    source = release_fixtures.SOURCE
    tag = '3.55.0-zh-CN.rc.3'

    def release(self, revision, **changes):
        return dict(dict(id=10 + revision, tag_name=f'3.55.0-zh-CN.rc.{revision}',
                         draft=False, prerelease=True), **changes)

    def client(self, releases=()):
        client = FamilyGitHubFixture()
        client.catalog = list(releases)
        return client

    def validate(self, client, tag=None):
        return native_promote.validate_promotion_source(client.api, self.source, tag or self.tag)

    def test_valid_successor_ignores_other_families_and_unpublished_drafts(self):
        client = self.client([self.release(2), self.release(30, draft=True),
                              self.release(999, tag_name='3.51.2-zh-CN.rc.999')])
        self.validate(client)
        self.assertEqual(client.writes, [])
        self.assertIn(('commits/refs%2Ftags%2F3.55.0-zh-CN.rc.2', 'GET'), client.calls)

    def test_revision_is_numeric_not_release_order(self):
        client = self.client([self.release(10), self.release(2)])
        for revision in (1, 3, 9):
            with self.subTest(revision=revision), self.assertRaisesRegex(ValueError, 'increment'):
                self.validate(client, f'3.55.0-zh-CN.rc.{revision}')
        self.validate(client, '3.55.0-zh-CN.rc.11')

    def test_published_target_is_never_treated_as_recoverable(self):
        client = self.client([self.release(3)])
        with self.assertRaisesRegex(ValueError, 'unpublished'):
            self.validate(client)
        self.assertEqual(client.writes, [])

    def test_same_sha_draft_or_orphan_tag_can_resume(self):
        client = self.client([self.release(2)])
        client.ref = {'object': {'type': 'commit', 'sha': self.source}}
        self.validate(client)
        client.release = self.release(3, draft=True, target_commitish=self.source)
        self.validate(client)
        client.catalog.append(self.release(4))
        with self.assertRaisesRegex(ValueError, 'increment'):
            self.validate(client)

    def test_draft_identity_missing_or_moved_tag_fails_before_writes(self):
        for ref in (None, {}, [], {'object': None}, {'object': {'type': 'tag', 'sha': self.source}},
                    {'object': {'type': 'commit', 'sha': 'c' * 40}}):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                client = self.client()
                client.release = self.release(3, draft=True, target_commitish=self.source)
                client.ref = ref
                self.validate(client)
            self.assertEqual(client.writes, [])
        for change in ({'target_commitish': 'c' * 40}, {'target_commitish': 'main'}, {'prerelease': False}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                client = self.client([dict(self.release(3, draft=True, target_commitish=self.source), **change)])
                client.ref = {'object': {'type': 'commit', 'sha': self.source}}
                self.validate(client)

    def test_behind_diverged_and_malformed_compare_results_fail_closed(self):
        client = self.client([self.release(2)])
        valid = dict(status='ahead', ahead_by=1, behind_by=0,
                     base_commit={'sha': client.latest_sha}, merge_base_commit={'sha': client.latest_sha})
        bad = [None, [], {}, dict(valid, status='behind'), dict(valid, status='diverged'),
               dict(valid, status='unknown'), dict(valid, behind_by=1), dict(valid, behind_by=False),
               dict(valid, ahead_by=True), dict(valid, ahead_by='1'), dict(valid, ahead_by=-1),
               dict(valid, status='identical'), dict(valid, status='identical', ahead_by=0),
               dict(valid, ahead_by=0),
               dict(valid, base_commit={'sha': 'c' * 40}), dict(valid, merge_base_commit=None),
               dict(valid, merge_base_commit={'sha': 'c' * 40})]
        for comparison in bad:
            with self.subTest(comparison=comparison), self.assertRaises(ValueError):
                client.comparisons[client.latest_sha] = comparison
                self.validate(client)
        client.comparisons[client.latest_sha] = valid
        self.validate(client)
        client.latest_sha = self.source
        self.validate(client)  # Repackaging a descendant at the same exact source is allowed.

    def test_historical_baseline_is_still_required_without_modern_releases(self):
        client = self.client()
        baseline = next(sha for version, _, sha in native_promote.RELEASES if version == '3.55.0')
        client.comparisons[baseline] = {'status': 'diverged'}
        with self.assertRaises(ValueError):
            self.validate(client)

    def test_latest_release_is_found_after_the_first_hundred(self):
        old = [dict(id=1000 + i, tag_name=f'unrelated-{i}', draft=False, prerelease=False) for i in range(100)]
        client = self.client(old + [self.release(2)])
        self.validate(client)
        self.assertIn(('releases?per_page=100&page=2', 'GET'), client.calls)
        self.assertIn(('commits/refs%2Ftags%2F3.55.0-zh-CN.rc.2', 'GET'), client.calls)

    def test_catalog_shape_duplicates_and_missing_metadata_fail_closed(self):
        valid = self.release(2)
        pages = [None, {}, 'not a page', [None], [[]], [dict(valid, id=True)],
                 [dict(valid, id=0)], [dict(valid, tag_name=None)], [dict(valid, tag_name='')],
                 [dict(valid, draft=None)], [dict(valid, prerelease='true')], [valid, valid],
                 [valid, dict(valid, id=999)], [valid, dict(valid, tag_name='other')], [valid] * 101]
        for rows in pages:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                native_promote.release_catalog(lambda path: rows)
        first = [dict(valid, id=100 + i, tag_name=f'other-{i}') for i in range(100)]
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            native_promote.release_catalog(lambda path: first if 'page=1' in path else [first[0]])

    def test_malformed_published_family_tags_and_unresolved_commits_fail(self):
        for tag in ('3.55.0-zh-CN.rc.0', '3.55.0-zh-CN.rc.01', '3.55.0-zh-CN.rc.1suffix'):
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, 'Malformed'):
                self.validate(self.client([self.release(2, tag_name=tag)]))
        client = self.client([self.release(2)])
        for sha in (None, 'main', 'A' * 40, [], 123):
            with self.subTest(sha=sha), self.assertRaisesRegex(ValueError, 'valid source commit'):
                client.latest_sha = sha
                self.validate(client)

    def assets(self):
        fixture = release_fixtures.NativeReleaseTests('test_five_zip_manifest_uses_final_names_and_excludes_ci_reports')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.prepare()
        return fixture.output

    def publish(self, client, directory, tag=None):
        return native_promote.publish_with_family_guard(client, directory, self.source,
                                                        tag or release_fixtures.TAG,
                                                        release_fixtures.review_for(directory))

    def test_guarded_publisher_keeps_add_only_interrupted_draft_recovery(self):
        directory = self.assets()
        client = self.client()
        client.fail_upload = 2
        with self.assertRaises(RuntimeError):
            self.publish(client, directory)
        self.assertTrue(client.release['draft'])
        client.fail_upload = None
        self.assertFalse(self.publish(client, directory)['draft'])
        self.assertEqual(len([write for write in client.writes if write[0] == 'upload']), 6)
        self.assertEqual(len([write for write in client.writes if write[:2] == ('git/refs', 'POST')]), 1)
        self.assertEqual(client.writes[-1][:2], ('releases/1', 'PATCH'))
        self.assertFalse(any(write[1] == 'DELETE' for write in client.writes))

    def test_new_release_during_readback_blocks_the_final_publication(self):
        directory = self.assets()
        client = self.client()
        client.on_download = lambda current: setattr(current, 'catalog', [self.release(2)])
        with self.assertRaisesRegex(ValueError, 'increment'):
            self.publish(client, directory)
        self.assertTrue(client.release['draft'])
        self.assertEqual(len(client.data), 6)
        self.assertFalse(any(write[1] == 'PATCH' for write in client.writes))
        self.assertGreaterEqual(client.calls.count(('releases?per_page=100&page=1', 'GET')), 3)

    def test_new_ancestor_during_readback_requires_inheritance_even_with_higher_rc(self):
        directory = self.assets()
        client = self.client([self.release(1)])
        def new_release(current):
            current.catalog = [self.release(1), self.release(2)]
            current.latest_sha = 'c' * 40
            current.comparisons[current.latest_sha] = {'status': 'diverged'}
        client.on_download = new_release
        with self.assertRaisesRegex(ValueError, 'descend'):
            self.publish(client, directory, self.tag)
        self.assertTrue(client.release['draft'])
        self.assertFalse(any(write[1] == 'PATCH' for write in client.writes))

    def test_api_failure_before_or_during_publication_fails_closed(self):
        directory = self.assets()
        client = self.client()
        original_api = client.api
        def unavailable(path, method='GET', data=None, missing=False):
            if path.startswith('releases?'):
                raise RuntimeError('Simulated unavailable GitHub catalog')
            return original_api(path, method, data, missing)
        with patch.object(client, 'api', side_effect=unavailable):
            with self.assertRaisesRegex(RuntimeError, 'unavailable'):
                self.publish(client, directory)
        self.assertEqual(client.writes, [])
        client.on_download = lambda current: setattr(current, 'api', unavailable)
        with self.assertRaisesRegex(RuntimeError, 'unavailable'):
            self.publish(client, directory)
        self.assertTrue(client.release['draft'])
        self.assertFalse(any(write[1] == 'PATCH' for write in client.writes))

    def test_invalid_family_source_stops_before_any_remote_mutation(self):
        directory = self.assets()
        client = self.client([self.release(2)])
        with self.assertRaisesRegex(ValueError, 'increment'):
            self.publish(client, directory)
        self.assertEqual(client.writes, [])


if __name__ == '__main__': unittest.main()
