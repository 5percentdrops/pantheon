#!/usr/bin/env bash
#
# install_budget_watcher.sh  (V8.7)
#
# Installs a cron entry for budget_watcher.py in ~/.hermes-arthur/cron/.
# Arthur owns budget oversight, so the watcher lives in Arthur's home
# only — not duplicated across 32 homes.
#
# Idempotent. Flags:
#   --dry-run     Print, don't write
#   --uninstall   Remove the cron entry
#   --interval N  Minutes between runs (default 30, max 60)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WATCHER="$ROOT/scripts/budget_watcher.py"

DRY_RUN=0
UNINSTALL=0
INTERVAL=30

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

if (( INTERVAL < 1 || INTERVAL > 60 )); then
  echo "--interval must be 1..60 (got $INTERVAL)" >&2
  exit 2
fi

ARTHUR_HOME="$HOME/.hermes-arthur"
if [[ ! -d "$ARTHUR_HOME" ]]; then
  echo "Arthur's home ($ARTHUR_HOME) not found — run bootstrap_hermes_homes.sh first." >&2
  exit 1
fi

CRON_FILE="$ARTHUR_HOME/cron/budget_watcher.cron"

if [[ "$UNINSTALL" == "1" ]]; then
  if [[ -f "$CRON_FILE" ]]; then
    if [[ "$DRY_RUN" == "1" ]]; then
      echo "[dry-run] would rm $CRON_FILE"
    else
      rm -f "$CRON_FILE"
      echo "removed: $CRON_FILE"
    fi
  else
    echo "no existing budget_watcher cron to remove"
  fi
  exit 0
fi

mkdir -p "$ARTHUR_HOME/cron"

body=$(cat <<EOF
# Pantheon V8.7 — per-host budget watcher (Arthur-owned)
# Sums per-agent today's token-proxy bytes, alerts on >=80% cap burn.
# Runs every $INTERVAL minutes.
*/$INTERVAL * * * *  python3 $WATCHER
EOF
)

if [[ "$DRY_RUN" == "1" ]]; then
  echo "[dry-run] would write $CRON_FILE:"
  echo "$body" | sed 's/^/    /'
else
  printf '%s\n' "$body" > "$CRON_FILE"
  chmod 600 "$CRON_FILE"
  echo "installed: $CRON_FILE (every $INTERVAL min)"
fi
