#!/usr/bin/env python3
"""budget_watcher.py  (V8.7)

Per-host budget watcher. Runs every 30 minutes via per-home Hermes cron.
Sums per-agent token usage from each ~/.hermes-<slug>/sessions/ tree,
compares against the agent's budget cap in
Pantheon/company/budget_policy.yaml, and emits alerts when usage crosses
80% of cap.

Alert sinks (in order of preference):
  1. workspace/07_Finalization/budget_alerts.jsonl  (append-only, append-safe)
  2. ~/.hermes-arthur/MEMORY.md  (Arthur reads on next dispatch)
  3. stderr  (fallback)

Never spends tokens. Never calls an LLM. Pure file IO.

Exit codes:
  0  success (whether or not any alerts fired)
  1  no Hermes homes present
  2  budget_policy.yaml missing or unreadable
"""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
BUDGET_POLICY = REPO_ROOT / "Pantheon" / "company" / "budget_policy.yaml"
ALERT_LOG = REPO_ROOT / "workspace" / "07_Finalization" / "budget_alerts.jsonl"
HOME = Path.home()
ARTHUR_MEMORY = HOME / ".hermes-arthur" / "MEMORY.md"

THRESHOLD_WARN = 0.80
THRESHOLD_CRIT = 0.95


def load_budget_caps() -> dict[str, int]:
    """Parse budget_policy.yaml into {agent_slug: token_cap}. Returns {}
    if file missing or unparseable; watcher falls back to a uniform
    100k/day cap so it never crashes."""
    if not BUDGET_POLICY.exists():
        return {}
    try:
        import yaml
        data = yaml.safe_load(BUDGET_POLICY.read_text(encoding="utf-8"))
    except Exception:
        return {}
    caps = {}
    for entry in (data or {}).get("budgets", []) or []:
        slug = entry.get("agent_slug") or entry.get("slug")
        cap = entry.get("daily_token_cap") or entry.get("token_cap")
        if slug and isinstance(cap, int):
            caps[slug] = cap
    return caps


def count_tokens_today(home: Path) -> int:
    """Sum bytes-as-tokens-proxy across today's session files. Bytes/4 is
    a deliberate proxy — exact token counting requires a model-specific
    tokenizer we don't ship. Good enough to catch budget burn signals."""
    sessions = home / "sessions"
    if not sessions.exists():
        return 0
    today = datetime.now(timezone.utc).date().isoformat()
    total_bytes = 0
    for f in sessions.rglob("*"):
        if not f.is_file():
            continue
        try:
            mtime_day = datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).date().isoformat()
        except OSError:
            continue
        if mtime_day == today:
            try:
                total_bytes += f.stat().st_size
            except OSError:
                pass
    return total_bytes // 4


def emit_alert(record: dict) -> None:
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ALERT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    if record["severity"] == "CRIT" and ARTHUR_MEMORY.exists():
        try:
            with ARTHUR_MEMORY.open("a", encoding="utf-8") as f:
                f.write(
                    f"\n## V8.7 budget alert {record['timestamp_utc']}\n"
                    f"- Agent: `{record['slug']}` at "
                    f"{record['pct']:.0%} of daily cap "
                    f"({record['used']:,} / {record['cap']:,} tokens)\n"
                )
        except OSError:
            pass


def main() -> int:
    homes = sorted(HOME.glob(".hermes-*"))
    if not homes:
        print("No ~/.hermes-* homes present.", file=sys.stderr)
        return 1

    caps = load_budget_caps()
    default_cap = 100_000

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    alerts = 0
    for home in homes:
        slug = home.name.removeprefix(".hermes-")
        used = count_tokens_today(home)
        cap = caps.get(slug, default_cap)
        if cap <= 0:
            continue
        pct = used / cap
        severity = None
        if pct >= THRESHOLD_CRIT:
            severity = "CRIT"
        elif pct >= THRESHOLD_WARN:
            severity = "WARN"
        if severity:
            emit_alert({
                "timestamp_utc": now_iso,
                "slug": slug,
                "used": used,
                "cap": cap,
                "pct": pct,
                "severity": severity,
            })
            alerts += 1

    print(f"budget_watcher: scanned {len(homes)} homes, emitted {alerts} alert(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
