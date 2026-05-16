#!/usr/bin/env bash
#
# install_metrics_cron.sh  (V8.9)
#
# Installs metrics_summary.py cron in ~/.hermes-arthur/cron/ at */15.
# Arthur owns observability — same agent who owns budget oversight.
#
# Flags:
#   --dry-run     Print, don't write
#   --uninstall   Remove the cron entry
#   --interval N  Minutes between runs (default 15, max 60)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
METRICS="$ROOT/scripts/metrics_summary.py"

DRY_RUN=0
UNINSTALL=0
INTERVAL=15

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
  echo "--interval must be 1..60 (got $INTERVAL)" >&2; exit 2
fi

ARTHUR_HOME="$HOME/.hermes-arthur"
if [[ ! -d "$ARTHUR_HOME" ]]; then
  echo "Arthur's home ($ARTHUR_HOME) not found — run bootstrap_hermes_homes.sh first." >&2
  exit 1
fi

CRON_FILE="$ARTHUR_HOME/cron/metrics_summary.cron"

if [[ "$UNINSTALL" == "1" ]]; then
  [[ -f "$CRON_FILE" ]] && { [[ "$DRY_RUN" == "1" ]] && echo "[dry-run] rm $CRON_FILE" || rm -f "$CRON_FILE"; echo "removed: $CRON_FILE"; } || echo "no existing metrics cron to remove"
  exit 0
fi

mkdir -p "$ARTHUR_HOME/cron"

body=$(cat <<EOF
# Pantheon V8.9 — central metrics rollup (Arthur-owned observability)
# Reads V8.6–V8.8 alert sinks, writes workspace/07_Finalization/metrics_dashboard.{md,json}
# Cadence: every $INTERVAL minutes.
*/$INTERVAL * * * *  python3 $METRICS
EOF
)

if [[ "$DRY_RUN" == "1" ]]; then
  echo "[dry-run] would write $CRON_FILE:"; echo "$body" | sed 's/^/    /'
else
  printf '%s\n' "$body" > "$CRON_FILE"; chmod 600 "$CRON_FILE"
  echo "installed: $CRON_FILE (every $INTERVAL min)"
fi
