#!/usr/bin/env python3
"""Execute dump naming and the real PNG/EPS write/manifest method with doubles.

The production DumpFileName, ScreenDumpLog definition and DumpWindow
body are compiled unchanged. Small image/window/file doubles make the result
observable without FLTK, a display, or a native OpenVSP build. Written files are
test markers, not screenshots; this is not graphical acceptance evidence.
"""

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from check_translation_catalog import strip_comments

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / 'src/gui_and_draw'
CXX = shutil.which('c++') or shutil.which('g++')


def definition(source, prefix, struct=False):
    """Read a complete top-level definition, retaining the production body."""
    start = source.index(prefix)
    end = source.index('\n}', start) + 2
    if struct:
        if source[end] != ';':
            raise ValueError('Missing struct terminator')
        end += 1
    return source[start:end]


@unittest.skipUnless(CXX, 'A C++11 compiler is required for the screen dump fixture')
class ScreenDumpNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='openvsp-screen-dump-')
        cls.root = Path(cls.temp.name)
        log = definition((GUI / 'ScreenBase.h').read_text(encoding='utf-8'),
                         'struct ScreenDumpLog', struct=True)
        dump = definition((GUI / 'ScreenBase.cpp').read_text(encoding='utf-8'),
                          'void VspScreen::DumpWindow(')
        naming = definition((GUI / 'ScreenBase.cpp').read_text(encoding='utf-8'),
                            'static string DumpFileName(')
        driver = r'''#include <cctype>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>
using std::string;
using std::vector;
using std::to_string;
static int shot = 0;
static string mode;
struct TestWindow { int w() { return 2; } int h() { return 3; } };
struct Fl_RGB_Image {
    unsigned char array[18] = {};
    int data_w() { return 2; }
    int data_h() { return 3; }
    int ld() { return 0; }
    int d() { return 3; }
};
struct Fl_Image_Surface {
    Fl_Image_Surface(int, int, int) {}
    void draw(TestWindow*) {}
    Fl_RGB_Image* image() { return new Fl_RGB_Image; }
};
static int stbi_write_png(const char* name, int, int, int, const void*, int) {
    if (shot == 0 && (mode == "png-fail" || mode == "both-fail")) { return 0; }
    FILE* out = std::fopen(name, "wb");
    if (!out) { return 0; }
    std::fprintf(out, "png fixture %d\n", shot);
    return std::fclose(out) == 0;
}
static FILE* fl_fopen(const char* name, const char* flags) {
    if (shot == 0 && (mode == "eps-fail" || mode == "both-fail")) { return nullptr; }
    return std::fopen(name, flags);
}
struct Fl_EPS_File_Surface {
    FILE* out;
    Fl_EPS_File_Surface(int, int, FILE* f) : out(f) {}
    void draw(TestWindow*) { std::fprintf(out, "eps fixture %d\n", shot); }
    int close() { return std::fclose(out); }
};
'''
        driver += naming + '\n' + log + r'''
struct VspScreen {
    TestWindow window;
    TestWindow* m_FLTK_Window = &window;
    void DumpWindow(const string& name, ScreenDumpLog& log);
};
'''
        driver += dump + r'''
int main(int argc, char** argv) {
    if (argc < 3) { return 2; }
    mode = argv[1];
    ScreenDumpLog log;
    if (mode == "names") {
        for (int i = 3; i < argc; ++i) {
            std::cout << "NAME\t" << DumpFileName(argv[i]) << "\n";
        }
        return 0;
    }
    log.m_Dir = argv[2];
    VspScreen screens[2];
    for (int i = 3; i < argc; ++i, ++shot) {
        screens[shot % 2].DumpWindow(argv[i], log);
    }
    for (const string& line : log.m_Lines) { std::cout << "FILE\t" << line << "\n"; }
    std::cout << "FAILED\t" << log.m_NumFailed << "\n";
}
'''
        (cls.root / 'driver.cpp').write_text(driver, encoding='utf-8')
        cls.binary = cls.root / 'screen-dump'
        result = subprocess.run([CXX, '-std=c++11', '-Wall', '-Wextra', '-Werror',
                                 '-I', str(GUI), str(cls.root / 'driver.cpp'),
                                 '-o', str(cls.binary)], text=True, capture_output=True)
        if result.returncode:
            cls.temp.cleanup()
            raise AssertionError(result.stdout + result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_fixture(self, mode, directory, *titles):
        result = subprocess.run([str(self.binary), mode, str(directory), *titles],
                                text=True, encoding='utf-8', capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.splitlines()

    def names(self, *titles):
        lines = self.run_fixture('names', self.root, *titles)
        return [line.removeprefix('NAME\t') for line in lines if line.startswith('NAME\t')]

    def test_ordinary_english_names_keep_upstream_spelling(self):
        self.assertEqual(self.names('Wing Gen', 'Wing XForm', 'Wing Mass', 'A0-B_2'),
                         ['Wing_Gen', 'Wing_XForm', 'Wing_Mass', 'A0_B_2'])

    def test_original_case_and_collisions_are_preserved(self):
        self.assertEqual(self.names('Wing Gen', 'wing gen', 'A/B', 'A B', 'A_2'),
                         ['Wing_Gen', 'wing_gen', 'A_B', 'A_B', 'A_2'])

    def test_actual_duplicate_writes_use_same_upstream_basename(self):
        with tempfile.TemporaryDirectory(dir=self.root) as directory:
            self.run_fixture('dump', directory, 'Wing Gen', 'Wing/Gen')
            self.assertEqual((Path(directory) / 'Wing_Gen.png').read_text(), 'png fixture 1\n')
            self.assertEqual((Path(directory) / 'Wing_Gen.eps').read_text(), 'eps fixture 1\n')

    def assert_dump(self, mode, missing):
        with tempfile.TemporaryDirectory(dir=self.root) as directory:
            lines = self.run_fixture(mode, directory, 'Wing Gen', 'Wing XForm', 'Wing Mass')
            entries = [line.split('\t')[1:] for line in lines if line.startswith('FILE\t')]
            self.assertIn(f'FAILED\t{len(missing)}', lines)
            stems = ['Wing_Gen', 'Wing_XForm', 'Wing_Mass']
            expected = {f'{stem}.{ext}': f'{ext} fixture {i}\n'
                        for i, stem in enumerate(stems) for ext in ('png', 'eps')
                        if (i, ext) not in missing}
            actual = {path.name: path.read_text(encoding='utf-8')
                      for path in Path(directory).iterdir()}
            self.assertEqual(actual, expected)
            self.assertEqual({entry[0] for entry in entries}, set(expected))
            self.assertEqual(len(entries), len(expected))
            self.assertTrue(all(entry[1:] == ['2', '3'] for entry in entries))

    def test_real_writer_pairs_formats_and_manifest_without_overwrites(self):
        self.assert_dump('dump', set())

    def test_failed_png_preserves_other_exports(self):
        self.assert_dump('png-fail', {(0, 'png')})

    def test_failed_eps_preserves_other_exports(self):
        self.assert_dump('eps-fail', {(0, 'eps')})

    def test_both_failed_formats_preserve_other_exports(self):
        self.assert_dump('both-fail', {(0, 'png'), (0, 'eps')})


class ScreenDumpNameSourceTests(unittest.TestCase):
    def test_all_screens_share_the_batch_log_and_each_dump_resets_it(self):
        code = strip_comments((GUI / 'ScreenDump.cpp').read_text(encoding='utf-8'))
        dump = definition(code, 'int ScreenDumper::Dump(')
        self.assertLess(dump.index('m_Log = ScreenDumpLog();'), dump.index('AddDumpGeoms();'))
        arguments = re.findall(r'->ScreenDump\(([^)]*)\)', code)
        self.assertGreaterEqual(len(arguments), 3)
        self.assertEqual({argument.strip() for argument in arguments}, {'m_Log'})
        base = strip_comments((GUI / 'ScreenBase.cpp').read_text(encoding='utf-8'))
        screen = definition(base, 'void VspScreen::ScreenDump(')
        self.assertRegex(screen, r'DumpWindow\(\s*GetDumpName\(\)\s*\+\s*path,\s*log\s*\)')
        self.assertIn('SnapshotTabCaption( c )', screen)
        self.assertIn('const std::string m_RawTitle;', base)
        self.assertIn('copy_label( VSPTranslate( title ).c_str() );', base)
        self.assertIn('return tab ? tab->RawTitle().c_str() : widget->label();', base)
        self.assertEqual(base.count('new LocalizedSnapshotTab('), 3)
        self.assertNotIn('ScreenDumpNames', screen)
        self.assertNotIn('m_FileNames', screen)


if __name__ == '__main__':
    unittest.main()
