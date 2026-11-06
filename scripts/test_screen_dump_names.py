#!/usr/bin/env python3
"""Execute dump naming and the real PNG/EPS write/manifest method with doubles.

The production ScreenDumpNames header, ScreenDumpLog definition and DumpWindow
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
        driver = r'''#include "ScreenDumpNames.h"
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
        driver += log + r'''
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
            std::cout << "NAME\t" << log.m_FileNames.Next(argv[i]) << "\n";
        }
        return 0;
    }
    if (mode == "reset") {
        log.m_FileNames.Next("Wing 常规");
        log.m_FileNames.Next("Wing 变换");
        log = ScreenDumpLog();
        std::cout << "NAME\t" << log.m_FileNames.Next("Wing 质量") << "\n";
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

    def test_same_length_chinese_labels_do_not_collide(self):
        self.assertEqual(self.names('Wing 常规', 'Wing 变换', 'Wing 质量'),
                         ['Wing_______', 'Wing________2', 'Wing________3'])

    def test_punctuation_and_repeated_titles_are_disambiguated(self):
        self.assertEqual(self.names('A B', 'A/B', 'A_B', 'A B'),
                         ['A_B', 'A_B_2', 'A_B_3', 'A_B_4'])

    def test_nested_tab_paths_and_duplicate_flattened_paths_are_unique(self):
        self.assertEqual(self.names('Wing 常规 高级', 'Wing 变换 网格',
                                    'Wing A B', 'Wing A B'),
                         ['Wing______________', 'Wing_______________2',
                          'Wing_A_B', 'Wing_A_B_2'])

    def test_case_only_collisions_are_safe_on_windows(self):
        self.assertEqual(self.names('Wing Gen', 'wing gen', 'WING GEN'),
                         ['Wing_Gen', 'wing_gen_2', 'WING_GEN_3'])

    def test_preexisting_numeric_suffix_is_reserved(self):
        self.assertEqual(self.names('A_2', 'A', 'A', 'a_3', 'a'),
                         ['A_2', 'A', 'A_3', 'a_3_2', 'a_4'])

    def test_later_natural_suffix_cannot_overwrite_allocated_suffix(self):
        self.assertEqual(self.names('A', 'A', 'A_2', 'a_2'),
                         ['A', 'A_2', 'A_2_2', 'a_2_3'])

    def test_non_ascii_bytes_and_path_separators_remain_ascii(self):
        names = self.names('Wing ψ', 'Wing β', 'Wing é', 'Wing 中文',
                           'Wing 🛩', r'Wing ../x\y:z')
        self.assertEqual(len(names), len(set(name.lower() for name in names)))
        for name in names:
            self.assertRegex(name, r'\A[A-Za-z0-9_]+\Z')

    def test_large_batch_is_unique_and_deterministic(self):
        titles = ['Wing 常规', 'Wing 变换', 'wing 质量', 'Wing_______2'] * 100
        first = self.names(*titles)
        self.assertEqual(len(first), 400)
        self.assertEqual(len({name.lower() for name in first}), 400)
        self.assertEqual(first, self.names(*titles))

    def test_reset_restores_first_name_for_a_new_batch(self):
        self.assertEqual(self.run_fixture('reset', self.root), ['NAME\tWing_______'])

    def assert_dump(self, mode, missing):
        with tempfile.TemporaryDirectory(dir=self.root) as directory:
            lines = self.run_fixture(mode, directory, 'Wing 常规', 'Wing 变换', 'Wing 质量')
            entries = [line.split('\t')[1:] for line in lines if line.startswith('FILE\t')]
            self.assertIn(f'FAILED\t{len(missing)}', lines)
            stems = ['Wing_______', 'Wing________2', 'Wing________3']
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

    def test_failed_png_does_not_release_the_shared_basename(self):
        self.assert_dump('png-fail', {(0, 'png')})

    def test_failed_eps_does_not_release_the_shared_basename(self):
        self.assert_dump('eps-fail', {(0, 'eps')})

    def test_both_failed_formats_still_reserve_the_basename(self):
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
        self.assertNotIn('ScreenDumpNames', screen)
        self.assertNotIn('m_FileNames', screen)


if __name__ == '__main__':
    unittest.main()
