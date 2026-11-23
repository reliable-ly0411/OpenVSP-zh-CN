import subprocess
import unittest
from unittest.mock import patch

from dev_pr_checks import choose, classify


class DevelopmentCheckScopeTests(unittest.TestCase):
    base = "a" * 40
    head = "b" * 40

    def choose_with(self, row, parents=None):
        parents = parents or f"{self.base} {self.head}".encode()
        with patch("dev_pr_checks.git", side_effect=[parents, b"x\0", row]):
            return choose("pull_request", "develop/3.55.0-zh-CN", self.base, "fix/test", "true")

    def test_docs_and_display(self):
        self.assertEqual(classify(["README_zh-CN.md"]), "docs")
        self.assertEqual(classify(["src/gui_and_draw/VSPChinese.cpp", "README.md"]), "display")
        self.assertEqual(self.choose_with(b"M\0README.md\0"), "docs")
        self.assertEqual(self.choose_with(b"M\0src/gui_and_draw/VSPChinese.cpp\0M\0README.md\0"), "display")

    def test_fail_closed(self):
        for path in [".github/workflows/build-localized-pr.yml", "scripts/backfill_build.sh",
                     "src/CMakeLists.txt", "src/gui_and_draw/GuiDevice.cpp", "LICENSE", "examples/model.vsp3"]:
            self.assertEqual(classify(["README.md", path]), "full")
        for row in [b"D\0README.md\0", b"A\0README.md\0", b"T\0README.md\0",
                    b"M\0README.md", b"M\0x\xff\0", b""]:
            self.assertEqual(self.choose_with(row), "full")
        self.assertEqual(self.choose_with(b"M\0README.md\0", b"b"*40+b" "+b"c"*40), "full")
        self.assertEqual(choose("pull_request", "main", self.base), "full")
        self.assertEqual(choose("workflow_call", "develop/test", self.base), "full")
        with patch("dev_pr_checks.git", side_effect=subprocess.CalledProcessError(1, ["git"])):
            self.assertEqual(choose("pull_request", "dev/test", self.base, "fix/test", "true"), "full")


    def test_main_routine_scope_keeps_admission_full(self):
        def main_choose(row, head="docs/readme", local="true", a=None, b=None):
            values=[f"{self.base} {self.head}".encode(), b"x\0", row]
            if a is not None: values += [a,b]
            with patch("dev_pr_checks.git",side_effect=values):
                return choose("pull_request","main",self.base,head,local)
        raw = "version one\n## 未发布\n\nNote\n\n## Release 1\nLocked\n".encode()
        revised = raw.replace(b"Note",b"Updated")
        row = b"M\0README_zh-CN.md\0"
        self.assertEqual(main_choose(row,a=raw,b=revised),"docs")
        self.assertEqual(main_choose(row,a=raw,b=revised.replace(b"Locked",b"Altered")),"full")
        self.assertEqual(main_choose(row,a=raw,b=revised.replace(b"version one",b"version two")),"full")
        self.assertEqual(main_choose(row,head="ci/release",a=raw,b=revised),"full")
        self.assertEqual(main_choose(row,local="false",a=raw,b=revised),"full")
        self.assertEqual(main_choose(b"M\0src/gui_and_draw/VSPChinese.cpp\0",head="fix/menu"),"display")
        self.assertEqual(main_choose(b"M\0LICENSE\0M\0README_zh-CN.md\0"),"full")
        self.assertEqual(choose("pull_request","develop/test",self.base,"fix/test","false"),"full")
        self.assertEqual(choose("pull_request","develop/test",self.base,"release/prep","true"),"full")
