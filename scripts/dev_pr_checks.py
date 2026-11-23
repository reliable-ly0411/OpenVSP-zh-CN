"""Conservative fast lanes for development-target GitHub pull requests only."""

import re
import subprocess
import sys

DOCS = frozenset({"README.md", "README_zh-CN.md"})
DISPLAY = frozenset({"src/gui_and_draw/VSPChinese.cpp", "src/gui_and_draw/VSPChinese.h"})


def classify(paths):
    paths = set(paths)
    if paths and paths <= DOCS:
        return "docs"
    if paths and paths <= DOCS | DISPLAY:
        return "display"
    return "full"


def git(*args):
    return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL)


def unreleased_only(before, after):
    def protected(text):
        left, exact, tail = text.partition(b"\n## " + "未发布".encode() + b"\n")
        if not exact:
            return None
        _, following, right = tail.partition(b"\n## ")
        return (left, following, right)
    a, b = protected(before), protected(after)
    return a is not None and a == b


def choose(event, base_ref, base_sha, head_ref="", same_repo="false"):
    is_main = (base_ref == "main" and
               head_ref.startswith(("docs/", "fix/", "feat/")))
    is_routine = head_ref.startswith(("docs/", "fix/", "feat/"))
    if (event != "pull_request" or same_repo != "true" or not is_routine or
            not (is_main or base_ref.startswith(("develop/", "dev/")))):
        return "full"
    if not re.fullmatch(r"[0-9a-f]{40}", base_sha):
        return "full"
    try:
        parents = git("show", "-s", "--format=%P", "HEAD").decode("ascii").split()
        if len(parents) != 2 or parents[0] != base_sha:
            return "full"
        diff = git("diff", "--name-only", "-z", "--no-renames", base_sha, "HEAD", "--")
        trees = git("diff", "--diff-filter=ACMRTUXBD", "--name-status", "-z",
                    "--no-renames", base_sha, "HEAD", "--").split(b"\0")
        # Only modifying existing files can use the fast path. A deletion/addition,
        # typechange or rename requires the default suite.
        if not diff or trees[-1] != b"" or len(trees) % 2 != 1:
            return "full"
        if any(status != b"M" for status in trees[:-1:2]):
            return "full"
        paths = {path.decode("utf-8") for path in trees[1:-1:2]}
        if is_main:
            readme = "README_zh-CN.md"
            if not paths <= DISPLAY | {readme}:
                return "full"
            if readme in paths and not unreleased_only(git("show", base_sha + ":" + readme),
                                                       git("show", "HEAD:" + readme)):
                return "full"
        return classify(paths)
    except (OSError, subprocess.CalledProcessError, UnicodeError):
        return "full"


if __name__ == "__main__":
    print(choose(*sys.argv[1:]) if len(sys.argv) == 6 else "full")
