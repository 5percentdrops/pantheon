#!/usr/bin/env bash
#
# install_observability_crons.sh  (V8.9)
#
# Installs three V8.9 observability cron entries:
#   - metrics_summary.py            every 15 min        -> Arthur home
#   - system_outcomes_tracker.py    Mon 06:00 UTC       -> Winston home
#   - redundant_work_detector.py    Sun 05:00 UTC       -> Winston home
#
# Flags:
#   --dry-run     Print, don't write
#   --uninstall   Remove all three entries

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
METRICS="$ROOT/scripts/metrics_summary.py"
OUTCOMES="$ROOT/scripts/system_outcomes_tracker.py"
REDUNDANT="$ROOT/scripts/redundant_work_detector.py"

DRY_RUN=0
UNINSTALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

ARTHUR_HOME="$HOME/.hermes-arthur"
WINSTON_HOME="$HOME/.hermes-winston"

for h in "$ARTHUR_HOME" "$WINSTON_HOME"; do
  if [[ ! -d "$h" ]]; then
    echo "Home $h not found — run bootstrap_hermes_homes.sh first." >&2; exit 1
  fi
done

ARTHUR_CRON="$ARTHUR_HOME/cron/metrics_summary.cron"
OUTCOMES_CRON="$WINSTON_HOME/cron/system_outcomes_weekly.cron"
REDUNDANT_CRON="$WINSTON_HOME/cron/redundant_work_weekly.cron"

if [[ "$UNINSTALL" == "1" ]]; then
  for f in "$ARTHUR_CRON" "$OUTCOMES_CRON" "$REDUNDANT_CRON"; do
    if [[ -f "$f" ]]; then
      [[ "$DRY_RUN" == "1" ]] && echo "[dry-run] rm $f" || rm -f "$f"
      echo "removed: $f"
    fi
  done
  exit 0
fi

mkdir -p "$ARTHUR_HOME/cron" "$WINSTON_HOME/cron"

write() {
  local file="$1"; local body="$2"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] would write $file:"; echo "$body" | sed 's/^/    /'
  else
    printf '%s\n' "$body" > "$file"; chmod 600 "$file"
    echo "installed: $file"
  fi
}

write "$ARTHUR_CRON" "$(cat <<EOF
# Pantheon V8.9 — central metrics rollup (every 15 min)
*/15 * * * *  python3 $METRICS
EOF
)"

write "$OUTCOMES_CRON" "$(cat <<EOF
# Pantheon V8.9 — weekly system outcomes scorecard (Mon 06:00 UTC)
0 6 * * 1  python3 $OUTCOMES
EOF
)"

write "$REDUNDANT_CRON" "$(cat <<EOF
# Pantheon V8.9 — weekly redundant-work scan (Sun 05:00 UTC)
0 5 * * 0  python3 $REDUNDANT
EOF
)"

echo
echo "Observability crons installed (Arthur + Winston homes)."
