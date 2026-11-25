#!/usr/bin/env bash
set -euo pipefail
root="$(pwd)"
old_controller=8dbb3a800b3f35b47aed677d39a76907a1bc3dd4
old_product=42ca95e36890a2f109783e0ef07af216bbd5f5eb
qa_tag=3.56.0-zh-CN.rc.18
qa_product=7d4182333d4e9b57b5061d4bc22ef552a33160f4
qa_tree=5f52c13a58bd7739188058cbce428de2f8429720
manifest_sha=3eafdba2617a83675850dda04084b4392597bb248dd6972a6322f8f25709dcd8
official=ca4958f2cf98d5e787a2a3fa37efb497e4903902
historical_path=.github/workflows/ci-openvsp-356-ubuntu-rc-package.yml
test "$BACKFILL_SHA" = "$qa_product"
test "$BACKFILL_TAG" = "$qa_tag"
test "$(git -C controller rev-parse HEAD)" = "$GITHUB_SHA"
test "$(git -C controller rev-parse HEAD^1)" = "$old_controller"
test "$(git -C controller rev-parse HEAD^2)" = "$qa_product"
test "$(git -C tooling rev-parse HEAD)" = "$VALIDATED_TOOLING_SHA"
test "$VALIDATED_TOOLING_SHA" = "84a52891c1226de03d5bc38a10259e6b142f834d"
test "$(git -C tooling-history rev-parse HEAD)" = "8c1a1b4e4dccf50185f68a33af18d22cf1b748b0"
test "$(git -C tooling rev-parse HEAD^1)" = "8c1a1b4e4dccf50185f68a33af18d22cf1b748b0"
test "$(git -C tooling diff --name-only HEAD^1 HEAD)" = scripts/native_verify.py

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
  --manifest controller/.github/openvsp-qa/rc18-platform-candidate.manifest --manifest-sha "$manifest_sha"
test -z "$(git -C source diff --name-only "$official" "$qa_product" -- src/python_api)"
test "$(git -C source rev-parse HEAD:THIRD_PARTY_NOTICES.md)" = "$(git -C source rev-parse "$old_product":THIRD_PARTY_NOTICES.md)"
. /etc/os-release
test "$ID" = ubuntu && test "$VERSION_ID" = 24.04
test "$(uname -m)" = x86_64
env -u GITHUB_OUTPUT SOURCE_SHA="$BACKFILL_SHA" NEW_TAG="$BACKFILL_TAG" python3 tooling/scripts/native_plan.py --source source
python3 -X utf8 source/scripts/check_localization_release.py --source source --expected-tag "$BACKFILL_TAG" --packaging-target ubuntu-24.04-amd64
python3 -m unittest discover -s source/scripts -p test_localized_release_identity.py -v
python3 -m unittest discover -s source/scripts -p test_airshow_356_models.py -v
