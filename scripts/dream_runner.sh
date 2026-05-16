#!/usr/bin/env bash
#
# dream_runner.sh  (V8.6)
#
# Per-agent nightly Dreaming pass. Invoked by cron from inside a
# specific HERMES_HOME. Does NOT span multiple agents — one home per call.
#
# Goal: review recent sessions, extract patterns, dedup the skill library,
# consolidate MEMORY.md. All of this is delegated to `hermes dream` if
# present, with a deterministic fallback that only touches the agent's
# own home (never the repo, never another agent).
#
# Exit codes:
#   0  success
#   1  hermes not on PATH / HERMES_HOME unset
#   2  doctor failed before dream
#   3  dream invocation failed

set -euo pipefail

: "${HERMES_HOME:?HERMES_HOME must be set by cron (per-agent root)}"

if ! command -v hermes >/dev/null 2>&1; then
  echo "[dream] hermes binary not found on PATH" >&2
  exit 1
fi

LOG_DIR="$HERMES_HOME/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/dream-$(date -u +%Y-%m-%d).log"

{
  echo "=== dream pass start: $(date -u +%FT%TZ) HOME=$HERMES_HOME ==="

  # Pre-flight: doctor must pass before we touch memory.
  if ! hermes doctor >/dev/null 2>&1; then
    echo "[dream] hermes doctor failed — refusing to dream on a broken home"
    exit 2
  fi

  # Preferred path: native hermes dream (if supported by installed version).
  if hermes dream --help >/dev/null 2>&1; then
    hermes dream \
      --review-sessions 7d \
      --extract-patterns \
      --dedup-skills \
      --consolidate-memory \
      --max-tokens 8000
    rc=$?
    if [[ $rc -ne 0 ]]; then
      echo "[dream] hermes dream returned $rc"
      exit 3
    fi
  else
    # Fallback: structural cleanup only. Never invents content, never
    # rewrites SOUL.md. Compacts MEMORY.md (>5000 lines) and dedups
    # skills by checksum.
    MEM="$HERMES_HOME/MEMORY.md"
    if [[ -f "$MEM" ]] && (( $(wc -l <"$MEM") > 5000 )); then
      cp "$MEM" "$MEM.pre-dream-$(date -u +%Y%m%dT%H%M%SZ).bak"
      tail -n 4000 "$MEM" > "$MEM.tmp" && mv "$MEM.tmp" "$MEM"
      echo "[dream] MEMORY.md tail-truncated to 4000 lines (backup written)"
    fi

    SKILLS="$HERMES_HOME/skills"
    if [[ -d "$SKILLS" ]]; then
      # Dedup by content hash (deterministic, preserves first occurrence).
      declare -A seen=()
      while IFS= read -r f; do
        h="$(sha256sum "$f" | awk '{print $1}')"
        if [[ -n "${seen[$h]:-}" ]]; then
          echo "[dream] dup skill removed: $f (matches ${seen[$h]})"
          rm -f "$f"
        else
          seen[$h]="$f"
        fi
      done < <(find "$SKILLS" -maxdepth 2 -type f -name '*.md')
    fi
  fi

  echo "=== dream pass end: $(date -u +%FT%TZ) ==="
} >>"$LOG" 2>&1

exit 0
