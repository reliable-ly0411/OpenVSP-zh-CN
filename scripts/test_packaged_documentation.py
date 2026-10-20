#!/usr/bin/env python3
"""Exercise new document installation and immutable/legacy package verification."""
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from urllib.parse import unquote, urlsplit

from backfill_package import verify


REPO = Path(__file__).resolve().parents[1]
MODULE = REPO / 'src/cmake/InstallLocalizedDocumentation.cmake'
MODELS = (
    'NASA_X-57_Maxwell_Simplified_CRM_v4.4.1.vsp3',
    'NASA_N2A_Hybrid_Wing_Body.vsp3',
    'Community_Vans_RV-12.vsp3',
    'NASA_Six-Passenger_Tiltwing_UAM.vsp3',
    'Uber_eCRM-002_Lift-Plus-Cruise.vsp3',
    'Community_F-A-18C_Hornet.vsp3',
    'Community_Joby_S4_eVTOL.vsp3',
    'Community_Kitty_Hawk_Heaviside_eVTOL.vsp3',
)


class PackagedDocumentationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.source = self.workspace / 'source'
        self.source.mkdir()
        self.files = {name: b'document\nsecond line\n' for name in (
            'README.md', 'README_zh-CN.md', 'AGENTS.md', 'LICENSE', 'CHANGELOG.md',
            'THIRD_PARTY_NOTICES.md',
        )}
        self.files.update({
            '.gitattributes': b'* text=auto\n*.vsp3 -text\n',
            'vspIcon.png': b'\x89PNG\x00\r\nicon',
            'docs/status.md': b'# Coverage\nUnreviewed pages remain listed.\n',
            'docs/evidence/license.json': b'{"license_version": null}\n',
            'docs/evidence/image.png': b'\x89PNG\x00\r\nkeep exact bytes',
            'src/help/html/index.html': b'<html>\nhelp\n</html>\n',
            'src/help/images/sample.png': b'\x89PNG\x00\r\nhelp image',
            'src/help/vsp_help': b'help resource\n',
            'src/help/github-pandoc.css': b'body {}\n',
            'examples/scripts/example.vspscript': b'// keep relative paths\n',
            'examples/textures/example.png': b'\x89PNG\x00\r\nexample texture',
            'examples/Complete_Aircraft/SOURCES_AND_LICENSES.md': b'license versions unresolved\n',
        })
        for name in MODELS:
            self.files['examples/Complete_Aircraft/' + name] = (
                '<model name="' + name + '">\nunchanged\n</model>\n'
            ).encode()
        for name, data in self.files.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Package documentation test')
        self.git('config', 'user.email', 'package@example.invalid')
        self.git('add', '.')
        self.git('commit', '-m', 'source')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.source), *args], stderr=subprocess.DEVNULL)

    def source_bytes(self, name, windows=False):
        if windows:
            return self.git('-c', 'core.autocrlf=true', '-c', 'core.eol=crlf',
                            'cat-file', '--filters', 'HEAD:' + name)
        return self.git('show', 'HEAD:' + name)

    def archive(self, windows=False, omit=(), changed=None, include_docs=True):
        changed = changed or {}
        target = self.workspace / 'package.zip'
        tracked = self.git('ls-files', '-z').decode().split('\0')
        with zipfile.ZipFile(target, 'w') as archive:
            for executable in ('vsp', 'vspscript', 'vspaero', 'vspviewer', 'vsploads'):
                archive.writestr('OpenVSP/' + executable + ('.exe' if windows else ''), b'fixture')
            for name in tracked:
                if not name or name == '.gitattributes' or name in omit:
                    continue
                if name.startswith('docs/') and not include_docs:
                    continue
                destination = name
                if name.startswith('examples/'):
                    destination = 'Official_Examples/' + name.removeprefix('examples/')
                elif name.startswith('src/help/html/'):
                    destination = 'help/' + Path(name).name
                elif name.startswith('src/help/'):
                    destination = name.removeprefix('src/')
                data = changed.get(name, self.source_bytes(name, windows))
                archive.writestr('OpenVSP/' + destination, data)
                if name.startswith(('examples/scripts/', 'examples/textures/')):
                    archive.writestr('OpenVSP/' + name.removeprefix('examples/'), data)
        return target

    def test_all_documents_and_eight_models_are_verified(self):
        for windows in (False, True):
            with self.subTest(windows=windows):
                self.assertGreater(verify(self.archive(windows), self.source, runtime_resources=True), 20)

    def test_missing_notice_or_nested_document_is_rejected(self):
        for name in ('THIRD_PARTY_NOTICES.md', 'docs/status.md',
                     'docs/evidence/license.json', 'docs/evidence/image.png'):
            with self.subTest(name=name):
                with self.assertRaises(KeyError):
                    verify(self.archive(omit=(name,)), self.source)

    def test_modified_notice_text_and_binary_are_rejected(self):
        for windows in (False, True):
            for name in ('THIRD_PARTY_NOTICES.md', 'docs/status.md',
                         'docs/evidence/license.json', 'docs/evidence/image.png'):
                with self.subTest(windows=windows, name=name):
                    with self.assertRaisesRegex(ValueError, 'Package differs from immutable source'):
                        verify(self.archive(windows, changed={name: b'changed\n'}), self.source)

    def test_every_community_model_remains_required_and_byte_exact(self):
        for model in MODELS:
            name = 'examples/Complete_Aircraft/' + model
            with self.subTest(model=model):
                with self.assertRaises(KeyError):
                    verify(self.archive(omit=(name,)), self.source)
                with self.assertRaisesRegex(ValueError, 'Package differs from immutable source'):
                    verify(self.archive(changed={name: b'altered model\n'}), self.source)

    def test_legacy_source_keeps_its_original_document_scope(self):
        self.git('rm', 'THIRD_PARTY_NOTICES.md')
        self.git('commit', '-m', 'fixture for old source without new notice')
        self.assertGreater(verify(self.archive(include_docs=False), self.source), 15)
        model = 'examples/Complete_Aircraft/' + MODELS[-1]
        with self.assertRaises(KeyError):
            verify(self.archive(include_docs=False, omit=(model,)), self.source)

    def test_source_bytes_come_from_commit_not_modified_checkout(self):
        (self.source / 'docs/status.md').write_bytes(b'uncommitted change\n')
        self.assertGreater(verify(self.archive(), self.source), 20)
        with self.assertRaisesRegex(ValueError, 'Package differs from immutable source'):
            verify(self.archive(changed={'docs/status.md': b'uncommitted change\n'}), self.source)

    def test_real_document_links_resolve_in_package_layout(self):
        documents = [REPO / name for name in ('README.md', 'README_zh-CN.md',
                     'THIRD_PARTY_NOTICES.md', 'examples/Complete_Aircraft/SOURCES_AND_LICENSES.md')]
        documents.extend((REPO / 'docs').rglob('*.md'))
        installed = {'README.md', 'README_zh-CN.md', 'AGENTS.md', 'LICENSE',
                     'CHANGELOG.md', 'vspIcon.png', 'THIRD_PARTY_NOTICES.md'}
        installed.update(path.relative_to(REPO).as_posix()
                         for path in (REPO / 'docs').rglob('*') if path.is_file())
        installed.update('Official_Examples/' + path.relative_to(REPO / 'examples').as_posix()
                         for path in (REPO / 'examples').rglob('*') if path.is_file())
        for source in documents:
            relative = source.relative_to(REPO).as_posix()
            if relative.startswith('examples/'):
                relative = 'Official_Examples/' + relative.removeprefix('examples/')
            for link in re.findall(r'\]\(([^)]+)\)', source.read_text(encoding='utf-8')):
                url = urlsplit(link)
                if url.scheme or url.netloc or not url.path:
                    continue
                destination = posixpath.normpath(posixpath.join(posixpath.dirname(relative),
                                                               unquote(url.path)))
                with self.subTest(document=relative, target=destination):
                    self.assertIn(destination, installed)

    @unittest.skipUnless(shutil.which('cmake'), 'CMake is required for isolated install test')
    def test_actual_cmake_module_installs_docs_and_all_examples(self):
        source_cmake = (REPO / 'src/CMakeLists.txt').read_text()
        call = 'INCLUDE( ${CMAKE_CURRENT_SOURCE_DIR}/cmake/InstallLocalizedDocumentation.cmake )'
        examples = 'INSTALL( DIRECTORY ../examples/ DESTINATION Official_Examples )'
        self.assertEqual(source_cmake.count(call), 1)
        self.assertEqual(source_cmake.count(examples), 1)
        module = self.source / 'src/cmake/InstallLocalizedDocumentation.cmake'
        module.parent.mkdir(parents=True)
        shutil.copyfile(MODULE, module)
        (self.source / 'src/CMakeLists.txt').write_text(
            'cmake_minimum_required(VERSION 3.24)\nproject(DocumentInstall NONE)\n'
            + examples + '\n' + call + '\n')
        build = self.workspace / 'build'
        install = self.workspace / 'install'
        subprocess.run(['cmake', '-S', str(self.source / 'src'), '-B', str(build)],
                       check=True, capture_output=True)
        subprocess.run(['cmake', '--install', str(build), '--prefix', str(install)],
                       check=True, capture_output=True)
        expected = {}
        for name, data in self.files.items():
            if name == 'THIRD_PARTY_NOTICES.md' or name.startswith('docs/'):
                expected[name] = data
            elif name.startswith('examples/'):
                expected['Official_Examples/' + name.removeprefix('examples/')] = data
        actual = {path.relative_to(install).as_posix(): path.read_bytes()
                  for path in install.rglob('*') if path.is_file()}
        self.assertEqual(actual, expected)
        for name, data in self.files.items():
            self.assertEqual((self.source / name).read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
