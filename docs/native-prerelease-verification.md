# Native prerelease verification

This document describes the new release gates, not a claim that any unrun platform has passed.
Old tags, published files and historical checksum manifests are never repaired in place.

## Two-stage workflow

1. Dispatch `native-prerelease.yml` at the reviewed tooling commit with `source_sha` and `new_tag`.
   The tag must be `<version>-zh-CN.rc.N`, with N a positive integer. The source must descend from
   the latest existing release in its family: 3.51.2 r7, 3.51.3 r2, 3.53.0, 3.54.0 r1, or 3.55.0 auto.
   Exact baseline commits remain in `scripts/backfill_plan.py`. Historical backfill targets and tools
   remain available by manual dispatch; pull requests run offline regression only, never native builds.
2. All five native jobs must succeed. The workflow never creates a tag or public Release.
3. Download the original `native-release-assets` artifact. Run `sha256sum -c SHA256SUMS.txt` and save
   the SHA-256 of the manifest itself. Review that exact Linux AMD64 ZIP, including the main window,
   wing page, and model names/paths. Screenshots still need a person to inspect their content.
4. Dispatch `native-promote.yml` with the original successful `build_run_id`, exact `source_sha`,
   `new_tag`, `manifest_sha256`, `linux_gui_sha256`, and an actual `validation_note` describing scope
   and limitations. No rebuild occurs. Original workflow/run/job identities, artifact transport
   digests, all five package reports, the manifest, and GUI acceptance hashes are checked again.
5. Promotion creates a new lightweight tag at the exact source and an unpublished prerelease draft.
   Existing draft files must match the original build bytes; only missing files may be uploaded.
   Every remote asset is downloaded by ID, checked against the original bytes, and checked using the
   actual `sha256sum -c SHA256SUMS.txt` command before the single public-state transition.

An interrupted draft is resumed by dispatching promotion again with the same build run and hashes.
Do not rerun compilation and try to overwrite the same draft with different bytes. A public Release,
conflicting tag, ambiguous draft, unexpected file or differing file causes a stop without deletion.
There is no multi-resource server transaction: failures may leave an incomplete **unpublished** draft,
but the add-only recovery never damages an earlier asset. Repository protection settings are not changed.

## Native targets and checks

| Runner | CPU | Python | NumPy |
|---|---|---|---|
| ubuntu-24.04 | x86_64 | distro 3.12 | 1.26.4 |
| ubuntu-24.04-arm | AArch64 | distro 3.12 | 1.26.4 |
| windows-2022 | x64 | 3.11 | 1.26.4 |
| macos-14 | ARM64 | 3.11 | 1.26.4 |
| macos-15-intel | x86_64 | 3.11 | 1.26.4 |

### Public archive name mapping

`scripts/native_plan.py:asset_name` is the single naming source for the new five-platform rc
packager, verification reports, release assembly, exact checksum list, promotion extraction and
Linux GUI hash binding. Public names use `OpenVSP-<version>-<archive platform>-zh-CN.zip` for each
supported family (3.51.2, 3.51.3, 3.53.0, 3.54.0 and 3.55.0). Internal platform/job IDs, runners,
architectures, Python versions and compiler choices are unchanged:

| Internal platform ID | Public archive platform |
|---|---|
| `Ubuntu-24.04_amd64` | `Ubuntu-24.04_amd64` |
| `Ubuntu-24.04_arm64-Python3.12` | `Ubuntu-24.04_arm64-Python3.12` |
| `win64` | `win64-Python3.11` |
| `macOS-14-arm64-Python3.11` | `macos-14-ARM64-Python3.11` |
| `macOS-15-x86_64-Python3.11` | `macos-15-intel-X64-Python3.11` |

The [official download page](https://openvsp.org/download.php), checked on 2026-10-19, links these
3.55.0 Python 3.11/Ubuntu 24.04 assets (the filenames below are taken from its actual link targets):

- `OpenVSP-3.55.0-win64-Python3.11.zip`
- `OpenVSP-3.55.0-macos-15-intel-X64-Python3.11.zip`
- `OpenVSP-3.55.0-macos-15-ARM64-Python3.11.zip`
- `OpenVSP-3.55.0-Ubuntu-24.04_amd64.deb`

Only the naming convention is adopted. This round keeps its actual macOS 14 ARM64 target instead
of claiming the official current macOS 15 target; no runner or minimum-OS upgrade is implied.
Ubuntu AMD64 remains a ZIP rather than pretending to be the official Debian package. Ubuntu ARM64
with Python 3.12 is an additional downstream build, not an official precompiled distribution.
The current official spellings are applied consistently across the five supported version families;
this does not claim that every historical upstream release provided the same target or package format.

Historical `backfill_*` names and legacy dual-platform naming remain unchanged. For new rc artifacts,
old Windows/Mac names, alternate spellings and extra files are rejected rather than normalized or
accepted as fallbacks. The public set remains exactly five ZIPs and `SHA256SUMS.txt`; the manifest,
reports and reviewed package hashes must bind these exact filenames and original bytes.

### macOS compiler and runner boundary

The current native matrix uses Homebrew LLVM 16 on both macOS targets. Before installation,
`native_macos_toolchain.py` requires the official `homebrew/core` formula to contain a bottle for the
actual named OS and CPU (`arm64_sonoma` or `sequoia`). Installation uses `--force-bottle`; the post-check
requires a bottled-install receipt, the planned keg version, and matching actual `clang` / `clang++`
versions and Mach-O architectures. Compiler hashes and host details go to the job summary and the
CI-only `toolchain.json`, not public Release assets. Historical backfill matrix/compiler choices are
unchanged. Other bundled dependencies still undergo the package-wide Mach-O minimum-OS check; a
dependency requiring a newer system fails the named target rather than silently raising compatibility.

As checked on 2026-10-19, [LLVM 16's official bottle metadata](https://formulae.brew.sh/api/formula/llvm@16.json)
includes Sonoma ARM64; [LLVM 18's metadata](https://formulae.brew.sh/api/formula/llvm@18.json) does not.
The check is performed again in each build because package availability can change.

[GitHub's macOS 14 retirement notice](https://github.com/actions/runner-images/issues/13518) sets
2026-11-02 as the final retirement date. The 2026-10-19 brownout runs from 14:00 UTC until 00:00 UTC
on October 20; jobs scheduled in that window fail. Further windows are listed in that notice.
After this release round, upgrade the native runner and revalidate dependency deployment targets,
package names and the stated minimum supported system together. A successful macOS 15 runtime check
does not establish that the same package runs on macOS 14. This patch keeps the current macOS 14 target
and makes no claim that a not-yet-run native build or GUI has passed.

### Package checks

- CLI: packaged `vsp -help` must succeed and contain Chinese usage. Only the exact old 3.51.x Linux
  X11 startup error may retry in Xvfb; other nonzero exits/timeouts remain failures.
- Model: baseline AngelScript smoke plus `localization_boundary_smoke.as` must preserve model names,
  identifiers, parameter values and special-character file paths across save/reopen.
  The shared `backfill_smoke.as` is taken from the pinned workflow tooling, because old source families
  predate that baseline script. Boundary and resource scripts are always taken from the exact source
  commit. A missing tooling baseline or either missing source script remains a failure, with no fallback.
  The slash-containing request follows upstream `ParmContainer::SetName`'s default slash removal:
  its accepted value is `Wing  Fuselage: Export_100%`. The other 13 names remain exact originals.
  The disk check compares accepted names; it does not redefine the upstream naming API.
  A failure emits CI-only `diagnostics/runtime.json` with the fixed script name, exit code, marker
  status, error categories and compile row/column numbers. Only predefined API spellings can be
  included as missing symbols; raw output, paths and model values are never copied into this report.
  Exact boundary failure lines preserve only six fixed reasons: `set_name`, `count`, `reloaded_name`,
  `lookup`, `parameter` and `api_error`. Unknown suffixes or lines containing values are ignored.
  Nonzero exit, timeout, missing success marker or any failure marker remain hard failures.
- Runtime resources: `localization_resources_smoke.as` runs from an empty cwd and clean home, discovers
  all ten official custom types, and creates a Cone. Both upstream top-level folders and the complete
  `Official_Examples` copy are checked against source bytes.
- Python: both `_vsp` and `_vsp_g` are imported in separate processes. A second, fresh venv installs
  **the actual packaged requirements**, runs `pip check`, imports installed `openvsp`, then imports both
  installed extensions. This catches ABI/dependency problems hidden by the build environment.
- Linux: every ELF machine must match the target; RPATH must be loader-relative, system dependencies
  must resolve to known distro packages, and system `libcminpack.so` is forbidden.
- macOS: recursively bundle non-system dylibs inside `python/openvsp/openvsp/lib`, rewrite loader-relative
  links, retain licenses, strip debug symbols, and ad-hoc sign and verify. The Python package manifest
  retains the closure during pip installation. Maximum Mach-O minimum OS must not exceed the named host.
  Non-system frameworks are rejected. There is no claim of Developer ID signing, notarization or
  Gatekeeper acceptance, or of compatibility below the measured Mach-O minimum.
- Windows: inspect every PE machine and imported/delay-imported DLL; require packaged, Windows system,
  API-set or the matching installed Python runtime dependency. Use a neutral build-drive alias so source
  paths do not expose private runner/workspace paths. Windows runtimes are not assumed to be bundled.
- Source: tracked source must remain unchanged. The report separately records actual full worktree
  status, so an untracked build folder is not misreported as a fully clean tree.
- Archives: CRC, duplicate/path traversal entries, source documents/examples/help byte equality,
  privacy scan, canonical filenames, full five-ZIP manifest and read-back hashes are checked.

## Evidence and public contents

Each native job uploads its ZIP and `verification.json`; macOS also retains `toolchain.json` in CI.
Assembly uploads exactly five final ZIPs plus
`SHA256SUMS.txt` as `native-release-assets`, and keeps `release-evidence.json` in the separate
`native-release-evidence` artifact. Optional Linux GUI screenshots have their own artifact and are not
an automated visual pass. These original build artifacts last 14 days. Promotion's `gui-review.json`
is kept separately for 30 days. No technical JSON, logs, screenshots or raw review notes are uploaded
to the public Release. The public body gives a short result summary and states GUI/platform boundaries.

The regression suite exercises invalid inputs, mixed-source/run artifacts, missing platforms/checks,
old/duplicate checksum names, wrong hashes, immutable public releases, conflicting tags, interrupted
uploads, add-only recovery, corruption on remote read-back, GUI hash mismatch, artifact provenance,
safe extraction, and official-tag/development-snapshot separation. Mocked tests do not replace native
platform runs or manual GUI review.

## Branch and workflow rollout

`build-localized-pr.yml` runs lightweight source guards, Python regressions and the small C++ localization
suite for PRs targeting main, develop/** or dev/**. Upstream candidates reuse these checks. Full native
builds are manual. GitHub must know the new dispatch workflow files on the default branch before the
Actions UI can launch them; merge the release-infrastructure change first, then dispatch it on a pinned
tooling ref with the separate reviewed development source SHA. This does not require merging the business
fixes into main or retagging any historical release.
