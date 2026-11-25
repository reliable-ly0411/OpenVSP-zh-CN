#!/usr/bin/env bash
set -euo pipefail
root="$(pwd)"
old_controller=8dbb3a800b3f35b47aed677d39a76907a1bc3dd4
old_product=42ca95e36890a2f109783e0ef07af216bbd5f5eb
qa_tag=3.56.0-zh-CN.rc.30
qa_product=c0e80e5ed135618fe78f55d72f2034ca7e3cf53d
qa_tree=040f63fab81a0dde4948224b36ffd2267182040e
manifest_sha=60f13372f21653ce55fe3325466cfa343d84626726b6574e1b5a8f45872684f6
official=ca4958f2cf98d5e787a2a3fa37efb497e4903902
historical_path=.github/workflows/ci-openvsp-356-ubuntu-rc-package.yml
test "$BACKFILL_SHA" = "$qa_product"
test "$BACKFILL_TAG" = "$qa_tag"
test "$(git -C controller rev-parse HEAD)" = "$GITHUB_SHA"
test "$(git -C controller rev-parse HEAD^1)" = "a61661ff0374db3415b88e95a33aa50aca2c6eb7"
test "$(git -C controller rev-parse HEAD^1^1)" = "d9846fe4c86477912f1a69f0557da3f4557b2740"
test "$(git -C controller rev-parse HEAD^1^1^1)" = "8830bd46c8c4230050d6da7a425102af826045bf"
test "$(git -C controller rev-parse HEAD^1^1^1^1)" = "54ebb91e28a6566e1fd8346eef3c5cdb218823ff"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1)" = "80e1c6b56f7c45168915d1e39477f98761dba14f"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1)" = "18ab5c34d246ea3125356ca8e7500acac07e01dc"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1)" = "f25cfdca8e5a9ca8a97f1cba46e8c93d20fdff5a"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1)" = "b4a83c362dc6373395a83b6c5c748b3add007b5c"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1^1)" = "1cfa0f883df96e53900873d99d63ed6302ea4d50"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1^1^1)" = "1ced5773949ba57b1be485d5f2426ffbdb7cf1db"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1)" = "4c3576a8ddc087c0559ec2c93c92e3089368d196"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1)" = "85aca522d18fc4bc5278f175a41fe2ddc7a5f5af"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "11c8776ccff99a75feba097900cad11ebe77ae5f"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "b157ced51daa14c510c49a70b7ee992a72caeba4"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "72b970d0c1527670253576d0a9329c8f3a4c1351"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "e478a6451eb83e29ef82673f820afd7c30d33d39"
test "$(git -C controller rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "$old_controller"
test "$(git -C controller rev-parse HEAD^3)" = "2cf18241ead9f8b7d780968de7688297be0370ef"
test "$(git -C controller rev-parse HEAD^2)" = "$qa_product"
test "$(git -C tooling rev-parse HEAD)" = "$VALIDATED_TOOLING_SHA"
test "$(git -C tooling rev-parse HEAD^1)" = "33daefa326b6bcd712f06d108473385435925171"
test "$(git -C tooling rev-parse HEAD^1^1)" = "897850aa4b5caafda7618e455d4c0152cfc017cf"
test "$(git -C tooling rev-parse HEAD^1^1^1)" = "494a0dd65ff7fab5f8f7035414354863250d2fe1"
test "$(git -C tooling rev-parse HEAD^1^1^1^1)" = "434d24137e065df6c8ce3766b75d9e98bf710759"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1)" = "853a9fcc6ccb95df1735694b97c6efdd34b8e5d0"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1)" = "ffaa322f0f89a556b601449e455487b7400c9851"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1)" = "a10eddbf4d52ef34c7c8a235c5f68d64dc452998"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1)" = "d26c28e85e9ead867d9b4064bfeb4f1b9c967455"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1^1)" = "1d475bc21d6d11b40b68c377391eb923aa264996"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1^1^1)" = "818444bc8446ea4ae3d48ef204e885c739b63f68"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1)" = "d4fb4f15c785cd5441c5b0ca7834c2a8c55aa554"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1)" = "29b328c50b9f9cd37e6cba67b63ebb8f0721fc61"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "0464597251ad1c167834d05a1ac1d25146909a2c"
test "$VALIDATED_TOOLING_SHA" = "2cf18241ead9f8b7d780968de7688297be0370ef"
test "$(git -C tooling-history rev-parse HEAD)" = "8c1a1b4e4dccf50185f68a33af18d22cf1b748b0"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "98f4cf781f4afcbfb176d83a8cade7c5fcea8b31"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "e6901ba03da11677802a837c734bf2d812005b3d"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "84a52891c1226de03d5bc38a10259e6b142f834d"
test "$(git -C tooling rev-parse HEAD^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1^1)" = "8c1a1b4e4dccf50185f68a33af18d22cf1b748b0"
test "$(git -C tooling diff --name-only HEAD^1 HEAD)" = "$(printf '%s\n' scripts/backfill_build.sh scripts/native_verify.py)"
test "$(git -C tooling diff --name-only 8c1a1b4e4dccf50185f68a33af18d22cf1b748b0 HEAD)" = "$(printf '%s\n' scripts/backfill_build.sh scripts/native_verify.py)"

# Replay every exact RC17 historical assertion on its own pinned checkout,
# never reducing the old guard to 'is a descendant'.
hist="$(mktemp -d "${RUNNER_TEMP:-/tmp}/openvsp-rc17-historical.XXXXXX")"
trap 'git -C "$root/source" worktree remove "$hist/source" >/dev/null 2>&1 || true; git -C "$root/controller" worktree remove "$hist/controller" >/dev/null 2>&1 || true' EXIT
git -C controller worktree add --detach "$hist/controller" "$old_controller"
git -C source worktree add --detach "$hist/source" "$old_product"
ln -s "$root/tooling-history" "$hist/tooling"
git -C "$hist/controller" show "HEAD:$historical_path" | python3 -c '
import sys
s=sys.stdin.read()
start="      - name: Verify exact product and existing release guards\n"
stop="      - name: Build and verify only the Ubuntu amd64 native ZIP\n"
before=s.split(start,1)[1].split(stop,1)[0].split("        run: |\n",1)[1]
assert all(line.startswith("          ") for line in before.splitlines())
sys.stdout.write("".join(line[10:]+"\n" for line in before.splitlines()))
' > "$hist/rc17-historical.sh"
echo "c85c12c4acdd1ced6d1b636f76555ec2b8cebb779d6bc39f84088e458b904359  $hist/rc17-historical.sh" | sha256sum -c -
(cd "$hist"; BACKFILL_SHA="$old_product" BACKFILL_TAG=3.56.0-zh-CN.rc.17 VALIDATED_TOOLING_SHA=8c1a1b4e4dccf50185f68a33af18d22cf1b748b0 GITHUB_SHA="$old_controller" bash rc17-historical.sh)

python3 controller/.github/openvsp-qa/check-current-parity.py \
  --source source --head "$qa_product" --tree "$qa_tree" \
  --manifest controller/.github/openvsp-qa/rc30-platform-candidate.manifest --manifest-sha "$manifest_sha"
test -z "$(git -C source diff --name-only "$official" "$qa_product" -- src/python_api)"
python3 - <<'INVENTORY'
from pathlib import Path
import subprocess
root = Path("source/src/gui_and_draw")
cmake = (root / "CMakeLists.txt").read_text()
registered = cmake.split("ADD_LIBRARY(gui_and_draw\n", 1)[1].split("\n)", 1)[0].splitlines()
tracked = set(subprocess.check_output(["git", "-C", "source", "ls-tree", "--name-only",
                                      "HEAD:src/gui_and_draw"], text=True).splitlines())
assert "ScreenDumpNames.h" not in registered and "ScreenDumpNames.h" not in tracked
assert set(registered) <= tracked and all((root / f).is_file() for f in registered)
INVENTORY
test "$(git -C source rev-parse HEAD:THIRD_PARTY_NOTICES.md)" = "$(git -C source rev-parse "$old_product":THIRD_PARTY_NOTICES.md)"
. /etc/os-release
test "$ID" = ubuntu && test "$VERSION_ID" = 24.04
test "$(uname -m)" = x86_64
env -u GITHUB_OUTPUT SOURCE_SHA="$BACKFILL_SHA" NEW_TAG="$BACKFILL_TAG" python3 tooling/scripts/native_plan.py --source source
python3 -X utf8 source/scripts/check_localization_release.py --source source --expected-tag "$BACKFILL_TAG" --packaging-target ubuntu-24.04-amd64
python3 -m unittest discover -s source/scripts -p test_localized_release_identity.py -v
python3 -m unittest discover -s source/scripts -p test_airshow_356_models.py -v
