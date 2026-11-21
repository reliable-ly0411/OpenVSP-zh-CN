"""Compile the exact Preview SetZoom handler against a small boundary harness."""

from pathlib import Path
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


class BackgroundPreviewZoomTest(unittest.TestCase):
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
