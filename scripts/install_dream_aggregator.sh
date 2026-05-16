#!/usr/bin/env bash
#
# install_dream_aggregator.sh  (V8.8)
#
# Installs Winston's nightly cross-agent dream aggregator at 04:00 UTC
# (1 hour after per-agent Dreaming at 03:00 UTC, so all per-home dreams
# have completed before Winston scrapes them).
#
# Flags:
#   --dry-run     Print, don't write
#   --uninstall   Remove the cron entry
#   --hour HH     Override hour (default 04, must be after Dreaming hour)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGG="$ROOT/scripts/dream_aggregator.py"

DRY_RUN=0
UNINSTALL=0
HOUR=04

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --hour) HOUR="$2"; shift 2 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

WINSTON_HOME="$HOME/.hermes-winston"
if [[ ! -d "$WINSTON_HOME" ]]; then
  echo "Winston's home ($WINSTON_HOME) not found — run bootstrap_hermes_homes.sh first." >&2
  exit 1
fi

CRON_FILE="$WINSTON_HOME/cron/dream_aggregator.cron"

if [[ "$UNINSTALL" == "1" ]]; then
  if [[ -f "$CRON_FILE" ]]; then
    if [[ "$DRY_RUN" == "1" ]]; then echo "[dry-run] rm $CRON_FILE"; else rm -f "$CRON_FILE"; fi
    echo "removed: $CRON_FILE"
  else
    echo "no existing dream_aggregator cron to remove"
  fi
  exit 0
fi

mkdir -p "$WINSTON_HOME/cron"

body=$(cat <<EOF
# Pantheon V8.8 — Winston cross-agent dream aggregator
# Runs 1h after per-agent Dreaming (03:00 UTC) so all dreams have flushed.
# Scrapes ~/.hermes-*/logs/dream-*.log + skills/*.md, dedups across
# agents by sha256, writes workspace/wiki/lessons_learned.md.
0 $HOUR * * *  python3 $AGG
EOF
)

if [[ "$DRY_RUN" == "1" ]]; then
  echo "[dry-run] would write $CRON_FILE:"
  echo "$body" | sed 's/^/    /'
else
  printf '%s\n' "$body" > "$CRON_FILE"
  chmod 600 "$CRON_FILE"
  echo "installed: $CRON_FILE (cadence: 0 $HOUR * * * UTC)"
fi
