#!/usr/bin/env bash
#
# bootstrap_hermes_homes.sh  (V8.5)
#
# Thin wrapper around bootstrap_hermes_homes.py that runs the converter first
# if needed, then optionally runs `hermes doctor` per home to verify.
#
# Flags (passed through to the Python script):
#   --dry-run               Print what would be written, no changes.
#   --only SLUG[,SLUG]      Limit to the given slugs.
#   --force-soul            Overwrite SOUL.md even if it exists.
#
# Local-only flags:
#   --skip-doctor           Don't run `hermes doctor` per home (default: run if hermes available).
#   --skip-converter        Don't auto-run convert_to_agentcompanies_v1.py.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG_DIR="$REPO_ROOT/software-house"

SKIP_DOCTOR=0
SKIP_CONVERTER=0
PASSTHRU=()

while [ $# -gt 0 ]; do
    case "$1" in
        --skip-doctor)    SKIP_DOCTOR=1 ;;
        --skip-converter) SKIP_CONVERTER=1 ;;
        --dry-run|--force-soul) PASSTHRU+=("$1") ;;
        --only) PASSTHRU+=("$1" "$2"); shift ;;
        -h|--help)
            sed -n '2,18p' "$0"
            exit 0
            ;;
        *) echo "Unknown flag: $1" >&2; exit 2 ;;
    esac
    shift
done

echo "==> SoftwareHouse V8.5 -> bootstrap Hermes homes"
echo

if [ "$SKIP_CONVERTER" = "0" ] && [ ! -d "$PKG_DIR" ]; then
    echo "==> Step 1/3: Generate software-house/ via converter"
    python3 "$REPO_ROOT/scripts/convert_to_agentcompanies_v1.py"
    echo
fi

echo "==> Step 2/3: Create per-agent Hermes homes"
python3 "$REPO_ROOT/scripts/bootstrap_hermes_homes.py" "${PASSTHRU[@]}"
echo

if [ "$SKIP_DOCTOR" = "1" ]; then
    echo "==> Step 3/3: skipped (hermes doctor)"
    exit 0
fi

if ! command -v hermes >/dev/null 2>&1; then
    echo "==> Step 3/3: hermes not on PATH — skipping doctor check."
    echo "Install Hermes Agent and re-run for per-home verification."
    exit 0
fi

echo "==> Step 3/3: hermes doctor per home"
fail_count=0
for home in "$HOME"/.hermes-*; do
    [ -d "$home" ] || continue
    slug="${home##*/.hermes-}"
    if HERMES_HOME="$home" hermes doctor >/dev/null 2>&1; then
        echo "  OK   $slug"
    else
        echo "  FAIL $slug  (HERMES_HOME=$home hermes doctor returned non-zero)"
        fail_count=$((fail_count + 1))
    fi
done

if [ "$fail_count" -gt 0 ]; then
    echo
    echo "WARNING: $fail_count homes failed hermes doctor. Investigate before importing to Paperclip."
    exit 1
fi
echo "All Hermes homes pass doctor."
