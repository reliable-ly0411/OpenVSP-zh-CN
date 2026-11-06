#!/usr/bin/env python3
"""Compile the real CLI parser with small dependency doubles, not the native GUI."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CXX = shutil.which('c++') or shutil.which('g++')


@unittest.skipUnless(CXX, 'A C++17 compiler is required for the CLI parser fixture')
class SnapshotCommandLineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='openvsp-cli-snapshot-')
        cls.root = Path(cls.temp.name)
        (cls.root / 'Vehicle.h').write_text('''#pragma once
#include <string>
#include <cstdio>
#include <cstdlib>
#include <cstring>
using std::string;
class Vehicle {
public:
    string filename, script;
    bool experimental = false;
    void SetVSP3FileName(const string &s) { filename = s; }
    int ReadXMLFile(const string &s) { return s == "missing.vsp3" ? 1 : 0; }
    int RunScript(const string &s) { script = s; return 17; }
    void SetExperimental(bool value) { experimental = value; }
};
''')
        (cls.root / 'main.h').write_text('''#pragma once
#define VSPVERSION1 "OpenVSP CLI test fixture"
enum { ESTATUS_NO_ERRORS = 0, ESTATUS_GENERAL_ERROR = 1, ESTATUS_INVALID_FILE_ERROR = 2 };
''')
        # Deliberately small counts exercise the real parser's bound checks.
        (cls.root / 'VSP_Geom_API.h').write_text('''#pragma once
namespace vsp { enum { VSP_NUM_SCREENS = 100, NUM_GEOM_SCREENS = 20 }; }
''')
        (cls.root / 'DesignVarMgr.h').write_text('''#pragma once
#include <string>
struct DesignVarManagerDouble {
    std::string des, xddm;
    void ReadDesVarsDES(const std::string &s) { des = s; }
    void ReadDesVarsXDDM(const std::string &s) { xddm = s; }
};
inline DesignVarManagerDouble DesignVarMgr;
''')
        (cls.root / 'driver.cpp').write_text('''#include "common.h"
#include "DesignVarMgr.h"
int main(int argc, char **argv) {
    Vehicle vehicle;
    ScreenDumpArgs dump;
    int status = -1;
    int mode = batchMode(argc, argv, &vehicle, status, dump);
    printf("\\nRESULT %d %d %d %d %d %.17g %d %d %d\\n", mode, status,
        dump.m_Dump, dump.m_Screen, dump.m_GeomScreen, dump.m_Scale,
        vehicle.experimental, !DesignVarMgr.des.empty(), !DesignVarMgr.xddm.empty());
}
''')
        cls.binary = cls.root / 'cli-parser'
        result = subprocess.run([CXX, '-std=c++17', '-I', str(cls.root), '-I', str(ROOT / 'src/vsp'),
            str(ROOT / 'src/vsp/common.cpp'), str(cls.root / 'driver.cpp'), '-o', str(cls.binary)],
            text=True, capture_output=True)
        if result.returncode:
            cls.temp.cleanup()
            raise AssertionError(result.stdout + result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_cli(self, *args):
        result = subprocess.run([str(self.binary), *args], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        marker, values = result.stdout.rsplit('\nRESULT ', 1)
        fields = values.split()
        self.assertEqual(len(fields), 9)
        return marker, dict(zip(('mode', 'status', 'dump', 'screen', 'geom', 'scale', 'exp', 'des', 'xddm'),
            [float(x) if i == 5 else int(x) for i, x in enumerate(fields)]))

    def test_chinese_help_keeps_every_snapshot_option(self):
        for flag in ('-help', '-h', '--help'):
            with self.subTest(flag=flag):
                output, result = self.run_cli(flag)
                self.assertIn('用法：vsp', output)
                self.assertIn('显示此帮助', output)
                for option in ('-snap [N]', '-snapgeom <N>', '-snapdir <目录>', '-snapscale <S>'):
                    self.assertIn(option, output)
                self.assertIn('PNG 和 EPS', output)
                self.assertEqual((result['mode'], result['status']), (1, 0))

    def test_snapshot_defaults_and_screen_selection(self):
        _, result = self.run_cli('-snap')
        self.assertEqual((result['dump'], result['screen'], result['geom'], result['scale']), (1, -1, -1, 1.0))
        _, result = self.run_cli('-snap', '3', '-snapscale', '2', '-snapgeom', '4')
        self.assertEqual((result['dump'], result['screen'], result['geom'], result['scale']), (1, 3, 4, 2.0))

    def test_invalid_snapshot_options_fail_in_chinese(self):
        for args, diagnostic in [
            (('-snap', '100'), '窗口编号'),
            (('-snapgeom',), '窗口编号'),
            (('-snapgeom', '20'), '窗口编号'),
            (('-snapgeom', '-1'), '窗口编号'),
            (('-snapdir',), '输出目录'),
            (('-snapscale',), '比例'),
            (('-snapscale', '0'), '比例'),
            (('-snapscale', '8.1'), '比例'),
            (('-snapscale', 'invalid'), '比例'),
        ]:
            with self.subTest(args=args):
                output, result = self.run_cli(*args)
                self.assertIn(diagnostic, output)
                self.assertEqual((result['mode'], result['status']), (1, 1))

    def test_output_directory_is_created_only_for_snapshot(self):
        with tempfile.TemporaryDirectory(dir=self.root) as directory:
            output = Path(directory) / '中文目录'
            self.run_cli('-snapdir', str(output))
            self.assertFalse(output.exists())
            _, result = self.run_cli('-snapdir', str(output), '-snap')
            self.assertTrue(output.is_dir())
            self.assertEqual(result['status'], 0)
            blocker = Path(directory) / 'not-a-directory'
            blocker.write_text('fixture')
            text, result = self.run_cli('-snap', '-snapdir', str(blocker))
            self.assertIn('无法创建目录', text)
            self.assertEqual((result['mode'], result['status']), (1, 1))

    def test_unreadable_model_fails_before_snapshot(self):
        output, result = self.run_cli('-snap', 'missing.vsp3')
        self.assertIn('无法读取 missing.vsp3', output)
        self.assertEqual((result['mode'], result['status']), (1, 2))

    def test_script_and_existing_options_remain_intact(self):
        _, result = self.run_cli('-script', 'test.as')
        self.assertEqual((result['mode'], result['status']), (1, 17))
        _, result = self.run_cli('-script', 'test.as', '-snap')
        self.assertEqual((result['mode'], result['status'], result['dump']), (0, 0, 1))
        _, result = self.run_cli('test.vsp3', '-des', 'test.des', '-xddm', 'test.xddm', '-exp')
        self.assertEqual((result['status'], result['des'], result['xddm'], result['exp']), (0, 1, 1, 1))


if __name__ == '__main__':
    unittest.main()
