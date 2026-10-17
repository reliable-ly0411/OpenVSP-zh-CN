#!/bin/sh
# Application-local font selection only; never edit system/user font settings.
set -eu
dir=$(CDPATH= cd -P -- "$(dirname -- "$0")" && pwd)
FONTCONFIG_FILE="$dir/openvsp-zh-fonts.conf"
export FONTCONFIG_FILE
if ! command -v fc-match >/dev/null 2>&1; then
    printf '%s\n' 'OpenVSP Chinese launcher requires fontconfig and fonts-noto-cjk.' >&2
    exit 1
fi
for alias in sans sans-serif Helvetica mono monospace Courier; do
    case "$alias" in
        mono|monospace|Courier) family='Noto Sans Mono CJK SC' ;;
        *) family='Noto Sans CJK SC' ;;
    esac
    actual=$(fc-match --format '%{family}' "$alias")
    case "$actual" in
        *"$family"*) ;;
        *) printf '%s\n' 'Required Chinese fonts unavailable: install fonts-noto-cjk.' >&2; exit 1 ;;
    esac
done
exec "$dir/vsp" "$@"
