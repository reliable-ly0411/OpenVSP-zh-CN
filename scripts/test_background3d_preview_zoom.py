"""Compile the exact Preview SetZoom handler against a small boundary harness."""

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREAMBLE = r"""
#include <cassert>
#include <cmath>
struct Param { int v; int operator()() const { return v; } };
struct Background3D {
    bool m_ImageReady;
    Param m_ImageW, m_ImageH;
    bool IsImageReady() const { return m_ImageReady; }
};
struct {
    Background3D *background = nullptr;
    Background3D *GetCurrentBackground3D() { return background; }
} Background3DMgr;
struct FakeGL {
    int w = 500, h = 500, zoom_calls = 0;
    double zoom = 0;
    int pixel_w() { return w; }
    int pixel_h() { return h; }
    FakeGL *getGraphicEngine() { return this; }
    FakeGL *getDisplay() { return this; }
    FakeGL *getCamera() { return this; }
    void relativeZoom(double v) { ++zoom_calls; zoom = v; }
};
struct Background3DPreviewScreen {
    FakeGL *m_GlWin;
    void SetZoom();
};
"""
TEST = r"""
int main() {
    FakeGL gl;
    Background3DPreviewScreen screen{&gl};
    screen.SetZoom(); // no background
    Background3D bg{false, {0}, {0}};
    Background3DMgr.background = &bg;
    screen.SetZoom(); // new background, no selection
    bg = {false, {192}, {128}};
    screen.SetZoom(); // old dimensions alone do not establish readiness
    bg = {true, {192}, {0}};
    screen.SetZoom(); // zero height, even if marked ready
    bg = {true, {0}, {128}};
    screen.SetZoom(); // zero width
    bg = {true, {192}, {128}};
    screen.m_GlWin = nullptr;
    screen.SetZoom();
    screen.m_GlWin = &gl;
    gl.w = 10;
    screen.SetZoom(); // viewport padding consumes the width
    gl.w = 500;
    gl.h = 9;
    screen.SetZoom();
    assert(gl.zoom_calls == 0);
    gl.h = 500;
    screen.SetZoom(); // wider image branch
    assert(gl.zoom_calls == 1 && std::isfinite(gl.zoom));
    assert(gl.zoom == 1.0 / 490.0);
    bg = {true, {128}, {192}};
    screen.SetZoom(); // taller image branch
    assert(gl.zoom_calls == 2 && std::isfinite(gl.zoom));
    assert(gl.zoom == 1.0 / (490.0 * (128.0 / 192.0)));
}
"""


ACCESS_PREAMBLE = r"""
#include <string>
#include <vector>
using std::string;
using std::vector;
using xmlNodePtr = void *;
class ParmContainer {};
struct Parm { double operator()() const; };
struct IntParm : Parm {};
struct BoolParm : Parm {};
struct DrawObj {};
"""


class BackgroundPreviewZoomTest(unittest.TestCase):
    def test_ui_guards_compile_with_real_background_access_specifiers(self):
        compiler = shutil.which('c++')
        if not compiler:
            self.skipTest('C++ compiler is required for the access check')
        # Compile the exact declaration with only its unrelated dependencies
        # stubbed. Keep the real access specifiers instead of making a mock
        # member public, which can conceal invalid access in the UI source.
        header = (ROOT / 'src/geom_core/Background3D.h').read_text(encoding='utf-8')
        declaration = '\n'.join(line for line in header.splitlines()
                                if not line.lstrip().startswith('#include'))
        guards = []
        for name, expected in [('ManageBackground3DScreen.cpp', 2), ('ScreenBase.cpp', 1)]:
            source = (ROOT / 'src/gui_and_draw' / name).read_text(encoding='utf-8')
            conditions = re.findall(r'^\s*if \( (.*->m_ImageW\(\).*->m_ImageH\(\).*) \)$',
                                    source, re.MULTILINE)
            self.assertEqual(len(conditions), expected, name)
            guards.extend(conditions)
        helpers = '\n'.join(
            f'bool guard_{i}(Background3D *bg3d, Background3D *bg3D, void *m_GlWin)'
            f' {{ return {condition}; }}'
            for i, condition in enumerate(guards)
        )
        with tempfile.TemporaryDirectory() as tmp:
            driver = Path(tmp) / 'access.cpp'
            driver.write_text(ACCESS_PREAMBLE + declaration + '\n' + helpers, encoding='utf-8')
            subprocess.run([compiler, '-std=c++11', '-fsyntax-only', str(driver)], check=True)

    def test_zoom_rejects_empty_and_padding_preserves_loaded_image_math(self):
        compiler = shutil.which('c++')
        if not compiler:
            self.skipTest('C++ compiler is required for the extracted handler harness')
        source = (ROOT / 'src/gui_and_draw/ScreenBase.cpp').read_text(encoding='utf-8')
        zoom = source.split('void Background3DPreviewScreen::SetZoom()', 1)[1]
        zoom = zoom.split('void Background3DPreviewScreen::ResizeCallBack', 1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            driver = Path(tmp) / 'zoom.cpp'
            binary = Path(tmp) / 'zoom'
            driver.write_text(PREAMBLE + 'void Background3DPreviewScreen::SetZoom()' + zoom + TEST,
                              encoding='utf-8')
            subprocess.run([compiler, '-std=c++11', str(driver), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
