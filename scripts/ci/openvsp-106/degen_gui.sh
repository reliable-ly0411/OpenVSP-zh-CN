#!/usr/bin/env bash
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
class_from_tree() {
  awk -v id="$1" '$1 == id && match($0, /\("[^"]+" "[^"]+"\)/) {
    print substr($0, RSTART, RLENGTH)
  }' "$2"
}
degen_ids_from_tree() {
  awk -v class="$1" 'index($0, class) && /[[:space:]]375x465[+-]/ {
    print $1
  }' "$2"
}
if [[ "${1:-}" == --session ]]; then
  shift
  bin=$1; fixture_path=$2; evidence=$3; mode=$4
  export HOME="$PWD/home" XDG_CONFIG_HOME="$PWD/home/config" XDG_CACHE_HOME="$PWD/home/cache"
  mkdir -p "$HOME"
  "$bin" "$fixture_path" > "$evidence/$mode-app.log" 2>&1 &
  pid=$!
  cleanup() {
    local rc=$?
    if (( rc != 0 )); then
      echo "Degen GUI session failed: $mode (exit $rc)" >&2
      xwininfo -root -tree > "$evidence/$mode-failure-windows.txt" 2>&1 || true
      timeout 5 import -window root "$evidence/$mode-failure.png" 2>/dev/null || true
      if [[ -s "$evidence/$mode-match.log" ]]; then cat "$evidence/$mode-match.log" >&2; fi
    fi
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    return "$rc"
  }
  trap cleanup EXIT
  main=
  for (( i=0; i<120; ++i )); do
    hits=$(xdotool search --onlyvisible --name 'OpenVSP .*fixture\.vsp3' 2>/dev/null || true)
    if [[ -n "$hits" && "$hits" != *$'\n'* ]]; then main=$hits; break; fi
    kill -0 "$pid"; sleep .25
  done
  if [[ -z "$main" ]]; then echo "$mode: unique OpenVSP main window not found" >&2; exit 1; fi
  main_xid=$(printf '0x%x' "$main")
  xwininfo -root -tree > "$evidence/$mode-main-windows.txt"
  main_class=$(class_from_tree "$main_xid" "$evidence/$mode-main-windows.txt")
  if [[ -z "$main_class" || "$main_class" == *$'\n'* ]]; then
    echo "$mode: could not resolve unique class for known main window $main_xid" >&2; exit 1
  fi
  printf '%s: main %s class %s\n' "$mode" "$main_xid" "$main_class"
  xdotool windowfocus "$main"
  # 458x720 main window's translated Analysis menu, then Degen Geom...
  xdotool mousemove --window "$main" 242 15 click 1 sleep .2 mousemove --window "$main" 262 173 click 1
  wid=
  for (( i=0; i<60; ++i )); do
    xwininfo -root -tree > "$evidence/$mode-windows.txt"
    hits=$(degen_ids_from_tree "$main_class" "$evidence/$mode-windows.txt")
    if [[ -n "$hits" && "$hits" != *$'\n'* ]]; then wid=$hits; break; fi
    kill -0 "$pid"; sleep .25
  done
  if [[ -z "$wid" ]]; then
    echo "$mode: no unique 375x465 Degen dialog of main class $main_class" >&2; exit 1
  fi
  printf '%s: Degen dialog %s\n' "$mode" "$wid"
  xdotool windowfocus "$wid"
  xdotool mousemove --window "$wid" 187 390 click 1
  # File IO completes synchronously in the GUI thread. Retry copying the actual FLTK
  # text buffer until it contains the expected terminal marker and whole message.
  for (( i=0; i<100; ++i )); do
    xdotool windowfocus "$wid"
    xdotool mousemove --window "$wid" 40 120 click 1 key --clearmodifiers ctrl+a ctrl+c
    timeout 2 xclip -selection clipboard -target UTF8_STRING -out > "$evidence/$mode-result.txt" 2>/dev/null || true
    if python3 "$here/verify.py" --clipboard "$mode" "$fixture_path" "$evidence/$mode-result.txt" > "$evidence/$mode-match.log" 2>&1; then break; fi
    kill -0 "$pid"; sleep .1
  done
  python3 "$here/verify.py" --clipboard "$mode" "$fixture_path" "$evidence/$mode-result.txt"
  xdotool mousemove --window "$wid" 5 120 click 1
  import -window "$wid" "$evidence/$mode-result.png"
  exit
fi

origin=$(realpath "$1"); candidate=$(realpath "$2"); evidence=$(realpath "$3"); scratch=$(realpath "$4")
seed="$scratch/degen-fixture-seed"
mkdir "$seed"
(cd "$seed" && "$origin/vspscript" -script "$here/fixture.as")
test -s "$seed/fixture.vsp3"
sha256sum "$seed/fixture.vsp3" > "$evidence/fixture.sha256"
cp "$seed/fixture.vsp3" "$evidence/fixture.vsp3"

# Run the same synthetic project in six fresh workdirs. A directory at the exact
# intended output name provokes a real fopen error (EISDIR), even on root runners.
for role in original candidate; do
  bin="$origin/vsp"; [[ "$role" != candidate ]] || bin="$candidate"
  for case_id in both csv-fails matlab-fails; do
    mode="$role-$case_id"
    case_dir="$scratch/$mode/Wing Design Export 100% 文件"
    mkdir -p "$case_dir"
    path="$case_dir/fixture.vsp3"
    cp "$seed/fixture.vsp3" "$path"
    case "$case_id" in
      csv-fails) mkdir "$case_dir/fixture_DegenGeom.csv" ;;
      matlab-fails) mkdir "$case_dir/fixture_DegenGeom.m" ;;
    esac
    (cd "$case_dir" && xvfb-run -a -s '-screen 0 1280x800x24' bash "$here/degen_gui.sh" --session "$bin" "$path" "$evidence" "$mode")
    for ext in csv m; do
      output="$case_dir/fixture_DegenGeom.$ext"
      if [[ -f "$output" ]]; then
        test -s "$output"
        cp "$output" "$evidence/$mode.$ext"
      else
        test -d "$output"
      fi
    done
  done
done
python3 "$here/verify.py" --exports "$evidence" | tee "$evidence/verification.txt"
