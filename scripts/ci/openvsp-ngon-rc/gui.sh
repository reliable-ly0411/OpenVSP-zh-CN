#!/usr/bin/env bash
set -euo pipefail
bin=$1; evidence=$2; tools=$3
export HOME="$PWD/home" XDG_CONFIG_HOME="$PWD/home/config" XDG_CACHE_HOME="$PWD/home/cache"
mkdir -p "$HOME"
"$bin" "$PWD/fixture.vsp3" > "$evidence/app.log" 2>&1 &
pid=$!
cleanup() {
  local status=$?
  xwininfo -root -tree > "$evidence/final-windows.txt" 2>&1 || true
  if (( status != 0 )); then timeout 5 import -window root "$evidence/failure.png" 2>/dev/null || true; fi
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  return "$status"
}
trap cleanup EXIT
win_by_size() {
  local size=$1 hits=
  for ((i=0; i<60; ++i)); do
    xwininfo -root -tree > "$evidence/window-scan.txt"
    hits=$(awk -v size="$size" 'index($0,"(\"vsp\" \"Vsp\")") && $0 ~ ("[[:space:]]" size "[+-]") {print $1}' "$evidence/window-scan.txt")
    if [[ -n "$hits" && "$hits" != *$'\n'* ]]; then printf '%s\n' "$hits"; return 0; fi
    kill -0 "$pid"; sleep .15
  done
  echo "No unique original OpenVSP window size $size" >&2
  return 1
}
click() {
  local w=$1 x=$2 y=$3
  xdotool windowfocus "$w" mousemove --window "$w" "$x" "$y" click 1 sleep .2
}
locate() {
  local w=$1 label=$2 stage=$3
  import -window "$w" -resize 200% "$evidence/$stage.png"
  tesseract "$evidence/$stage.png" "$evidence/$stage" -l chi_sim+eng --psm 11 tsv 2>"$evidence/$stage-tesseract.log"
  python3 "$tools/locate.py" "$evidence/$stage.tsv" "$label"
}
main=
for ((i=0; i<120; ++i)); do
  hits=$(xdotool search --onlyvisible --name 'OpenVSP .*fixture\.vsp3' 2>/dev/null || true)
  if [[ -n "$hits" && "$hits" != *$'\n'* ]]; then main=$hits; break; fi
  kill -0 "$pid"
  sleep .2
done
test -n "$main"
click "$main" 242 15
click "$main" 262 173
degen=$(win_by_size 375x465)
click "$degen" 357 417
# Original RC state fixed coordinates for closed/toggled Degen dropdown:
# prior screenshot verified Triangle at desktop y437 and N-Gon at y457, y-origin 20.
xdotool mousemove --window "$degen" 306 437 click 1 sleep .2
click "$degen" 104 416
import -window root "$evidence/degen-generated.png"
browser=$(win_by_size 275x671)
coords=$(locate "$browser" MeshGeom_NGon browser)
read -r x y <<< "$coords"
click "$browser" "$x" "$y"
editor=$(win_by_size 400x800)
coords=$(locate "$editor" 其他 editor-tabs)
read -r x y <<< "$coords"
click "$editor" "$x" "$y"
coords=$(locate "$editor" '写入VSPGEOM' editor-actions)
read -r x y <<< "$coords"
click "$editor" "$x" "$y"
chooser=$(win_by_size 440x345)
import -window "$chooser" "$evidence/write-vspgeom-chooser.png"
test ! -e dedicated-ngon.vspgeom
click "$chooser" 215 302
xdotool key --clearmodifiers ctrl+a
xdotool type --clearmodifiers 'dedicated-ngon.vspgeom'
click "$chooser" 75 327
for ((i=0; i<50; ++i)); do
  if [[ -s dedicated-ngon.vspgeom && -s dedicated-ngon.vkey ]]; then break; fi
  kill -0 "$pid"; sleep .15
done
python3 "$tools/check.py" "$PWD/dedicated-ngon.vspgeom" "$PWD/dedicated-ngon.vkey" | tee "$evidence/verification.txt"
cp fixture.vsp3 dedicated-ngon.* "$evidence/"
