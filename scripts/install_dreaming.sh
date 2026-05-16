#!/usr/bin/env bash
#
# install_dreaming.sh  (V8.6)
#
# Installs a nightly `dream_runner.sh` cron entry inside every
# ~/.hermes-<slug>/cron/ directory created by bootstrap_hermes_homes.sh.
#
# Idempotent. Re-runs replace the existing dream.cron with the current
# template. Does not enable system-level cron registration — Hermes reads
# its own per-home cron/ on startup.
#
# Flags:
#   --dry-run        Print what would be written, no changes.
#   --hour HH        Override default schedule hour (UTC, default 03).
#   --only SLUG[,..] Limit to specific agent slugs.
#   --uninstall      Remove dream.cron from every home.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DREAM_RUNNER="$ROOT/scripts/dream_runner.sh"

DRY_RUN=0
HOUR=03
ONLY=""
UNINSTALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --hour) HOUR="$2"; shift 2 ;;
    --only) ONLY="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

if [[ ! -x "$DREAM_RUNNER" ]]; then
  chmod +x "$DREAM_RUNNER" 2>/dev/null || true
fi

shopt -s nullglob
homes=("$HOME"/.hermes-*)
if (( ${#homes[@]} == 0 )); then
  echo "No ~/.hermes-* homes found. Run bootstrap_hermes_homes.sh first." >&2
  exit 1
fi

count=0
for home in "${homes[@]}"; do
  slug="${home##*/.hermes-}"
  if [[ -n "$ONLY" ]] && [[ ",$ONLY," != *",$slug,"* ]]; then
    continue
  fi
  cron_dir="$home/cron"
  cron_file="$cron_dir/dream.cron"

  if [[ "$UNINSTALL" == "1" ]]; then
    if [[ -f "$cron_file" ]]; then
      if [[ "$DRY_RUN" == "1" ]]; then echo "[dry-run] rm $cron_file"; else rm -f "$cron_file"; fi
      echo "uninstall: $slug"
      count=$((count + 1))
    fi
    continue
  fi

  mkdir -p "$cron_dir"

  body=$(cat <<EOF
# Pantheon V8.6 — nightly Dreaming pass for agent: $slug
# Reviews 7d of sessions, dedups skills, consolidates MEMORY.md.
# Owner: Hermes per-home scheduler (NOT system cron).
0 $HOUR * * *  HERMES_HOME=$home bash $DREAM_RUNNER
EOF
)

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] would write $cron_file:"
    echo "$body" | sed 's/^/    /'
  else
    printf '%s\n' "$body" > "$cron_file"
    chmod 600 "$cron_file"
    echo "install: $slug  ->  $cron_file"
  fi
  count=$((count + 1))
done

echo
if [[ "$UNINSTALL" == "1" ]]; then
  echo "Dreaming uninstalled from $count home(s)."
else
  echo "Dreaming installed in $count home(s). Schedule: 0 $HOUR * * * (UTC)."
fi
