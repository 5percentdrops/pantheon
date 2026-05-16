#!/usr/bin/env python3
"""metrics_summary.py  (V8.9) — Central observability rollup

Article Step 7: "Multi-agent systems are more complex than single agents.
More things can go wrong. Monitoring is not optional."

V8.7-V8.8 emitted alerts to scattered sinks. V8.9 rolls them up into one
dashboard you can read in 10 seconds.

Inputs (read-only; the watchers own writes):
  workspace/07_Finalization/budget_alerts.jsonl          (V8.7)
  workspace/05_QA_Audit_Logs/escalation_packet_rejections.jsonl   (V8.8)
  workspace/05_QA_Audit_Logs/escalation_packets.jsonl    (V8.8)
  workspace/05_QA_Audit_Logs/maxwell_override_grades.jsonl (V8.8)
  workspace/05_QA_Audit_Logs/outcome_grades.jsonl        (V8.7)
  workspace/wiki/lessons_learned.index.json              (V8.8)
  ~/.hermes-*/logs/dream-*.log                           (V8.6)
  ~/.hermes-*/sessions/                                  (size-only proxy)

Output:
  workspace/07_Finalization/metrics_dashboard.md         (human-readable)
  workspace/07_Finalization/metrics_dashboard.json       (machine-readable)

Pure file IO. No LLM calls. No agent state mutation.

Exit codes:
  0  success
  1  no workspace/ present yet
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = REPO_ROOT / "workspace"
HOME = Path.home()
OUT_MD = WORKSPACE / "07_Finalization" / "metrics_dashboard.md"
OUT_JSON = WORKSPACE / "07_Finalization" / "metrics_dashboard.json"

WINDOW_HOURS_RECENT = 24
WINDOW_HOURS_WEEK = 168


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def within(row: dict, hours: int, key: str = "timestamp_utc") -> bool:
    ts = parse_iso(row.get(key))
    if not ts:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return ts >= cutoff


def sessions_size_today(home: Path) -> int:
    sessions = home / "sessions"
    if not sessions.exists():
        return 0
    today = datetime.now(timezone.utc).date().isoformat()
    total = 0
    for f in sessions.rglob("*"):
        if not f.is_file():
            continue
        try:
            mtime_day = datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).date().isoformat()
            if mtime_day == today:
                total += f.stat().st_size
        except OSError:
            pass
    return total


def main() -> int:
    if not WORKSPACE.exists():
        print(f"metrics_summary: {WORKSPACE} not present — run installer first.", file=sys.stderr)
        return 1

    audit_dir = WORKSPACE / "05_QA_Audit_Logs"
    fin_dir = WORKSPACE / "07_Finalization"
    fin_dir.mkdir(parents=True, exist_ok=True)

    budget = read_jsonl(fin_dir / "budget_alerts.jsonl")
    rejections = read_jsonl(audit_dir / "escalation_packet_rejections.jsonl")
    escalations = read_jsonl(audit_dir / "escalation_packets.jsonl")
    maxwell_grades = read_jsonl(audit_dir / "maxwell_override_grades.jsonl")
    outcome_grades = read_jsonl(audit_dir / "outcome_grades.jsonl")

    lessons_idx_path = WORKSPACE / "wiki" / "lessons_learned.index.json"
    lessons_count = 0
    lessons_reinforced = 0
    if lessons_idx_path.exists():
        try:
            lessons = json.loads(lessons_idx_path.read_text(encoding="utf-8"))
            lessons_count = len(lessons)
            lessons_reinforced = sum(1 for v in lessons.values() if len(v.get("agents", [])) > 1)
        except (json.JSONDecodeError, OSError):
            pass

    homes = sorted(HOME.glob(".hermes-*"))
    homes_with_dream_today = 0
    dream_failures_24h = 0
    for h in homes:
        logs = list((h / "logs").glob("dream-*.log")) if (h / "logs").exists() else []
        for f in logs:
            try:
                if datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).date() == datetime.now(timezone.utc).date():
                    homes_with_dream_today += 1
                    text = f.read_text(encoding="utf-8", errors="replace")
                    if "FAIL" in text.upper() or "ERROR" in text.upper():
                        dream_failures_24h += 1
                    break
            except OSError:
                pass

    sessions_today_bytes = sum(sessions_size_today(h) for h in homes)

    # Roll up
    metrics = {
        "snapshot_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_recent_hours": WINDOW_HOURS_RECENT,
        "window_week_hours": WINDOW_HOURS_WEEK,
        "homes_total": len(homes),
        "homes_dreamed_today": homes_with_dream_today,
        "dream_failures_24h": dream_failures_24h,
        "sessions_bytes_today": sessions_today_bytes,
        "sessions_tokens_today_proxy": sessions_today_bytes // 4,
        "budget": {
            "alerts_24h": sum(1 for r in budget if within(r, WINDOW_HOURS_RECENT)),
            "alerts_7d":  sum(1 for r in budget if within(r, WINDOW_HOURS_WEEK)),
            "crit_24h":   sum(1 for r in budget if within(r, WINDOW_HOURS_RECENT) and r.get("severity") == "CRIT"),
            "warn_24h":   sum(1 for r in budget if within(r, WINDOW_HOURS_RECENT) and r.get("severity") == "WARN"),
        },
        "escalations": {
            "total_24h": sum(1 for r in escalations if within(r, WINDOW_HOURS_RECENT)),
            "total_7d":  sum(1 for r in escalations if within(r, WINDOW_HOURS_WEEK)),
            "rejected_packets_24h": sum(1 for r in rejections if within(r, WINDOW_HOURS_RECENT)),
            "rejection_rate_pct": _rate(rejections, escalations, WINDOW_HOURS_RECENT),
        },
        "outcomes": {
            "graded_24h": sum(1 for r in outcome_grades if within(r, WINDOW_HOURS_RECENT)),
            "passed_24h": sum(1 for r in outcome_grades if within(r, WINDOW_HOURS_RECENT) and r.get("decision") == "pass_to_cody"),
            "returned_24h": sum(1 for r in outcome_grades if within(r, WINDOW_HOURS_RECENT) and r.get("decision") == "return_to_jack"),
            "pass_rate_pct": _pass_rate(outcome_grades, WINDOW_HOURS_RECENT),
        },
        "maxwell_overrides": {
            "graded_24h": sum(1 for r in maxwell_grades if within(r, WINDOW_HOURS_RECENT)),
            "passed_24h": sum(1 for r in maxwell_grades if within(r, WINDOW_HOURS_RECENT) and r.get("decision") == "pass_to_cody"),
            "escalated_to_magnus_24h": sum(1 for r in maxwell_grades if within(r, WINDOW_HOURS_RECENT) and r.get("decision") == "escalate"),
        },
        "cross_agent_learning": {
            "lessons_total": lessons_count,
            "lessons_multi_agent_reinforced": lessons_reinforced,
        },
    }

    # Watch list — article Step 7 explicit failure modes
    watch = []
    if metrics["dream_failures_24h"] > 0:
        watch.append(f"🔴 {metrics['dream_failures_24h']} Dreaming failure(s) in last 24h")
    if metrics["budget"]["crit_24h"] > 0:
        watch.append(f"🔴 {metrics['budget']['crit_24h']} CRIT budget alert(s) in last 24h")
    if metrics["escalations"]["rejection_rate_pct"] is not None and metrics["escalations"]["rejection_rate_pct"] > 25:
        watch.append(f"🔴 escalation packet rejection rate {metrics['escalations']['rejection_rate_pct']}% > 25% threshold (engineers not formatting packets)")
    if metrics["outcomes"]["pass_rate_pct"] is not None and metrics["outcomes"]["pass_rate_pct"] < 50 and metrics["outcomes"]["graded_24h"] >= 4:
        watch.append(f"🟡 outcome rubric pass rate {metrics['outcomes']['pass_rate_pct']}% < 50% (Jack iterating heavily — check rubric calibration)")
    if metrics["maxwell_overrides"]["escalated_to_magnus_24h"] > 0:
        watch.append(f"🟡 {metrics['maxwell_overrides']['escalated_to_magnus_24h']} Maxwell override(s) escalated to Magnus (architecture itself suspect)")
    if metrics["homes_total"] > 0 and metrics["homes_dreamed_today"] < metrics["homes_total"] - 1:   # Owen excluded
        watch.append(f"🟡 only {metrics['homes_dreamed_today']}/{metrics['homes_total']-1} homes dreamed today (expected: all except Owen)")
    if not watch:
        watch.append("✅ no monitored failure modes triggered in last 24h")

    metrics["watch_list"] = watch

    # Write JSON
    OUT_JSON.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")

    # Write Markdown
    md = [
        "# Pantheon Metrics Dashboard",
        "",
        f"_Snapshot: {metrics['snapshot_utc']} UTC._",
        f"_Auto-generated by `scripts/metrics_summary.py` (V8.9). Read-only roll-up across V8.6–V8.8 alert sinks._",
        "",
        "## 🚨 Watch list (last 24h)",
        "",
    ]
    md.extend(f"- {w}" for w in watch)
    md += [
        "",
        "## 📊 Headline numbers",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Homes total | {metrics['homes_total']} |",
        f"| Homes dreamed today | {metrics['homes_dreamed_today']} |",
        f"| Dreaming failures (24h) | {metrics['dream_failures_24h']} |",
        f"| Sessions tokens today (byte/4 proxy) | {metrics['sessions_tokens_today_proxy']:,} |",
        f"| Lessons learned (cumulative) | {metrics['cross_agent_learning']['lessons_total']:,} |",
        f"| Lessons reinforced across ≥2 agents | {metrics['cross_agent_learning']['lessons_multi_agent_reinforced']:,} |",
        "",
        "## 💰 Budget (V8.7 watcher)",
        "",
        f"- WARN alerts 24h: {metrics['budget']['warn_24h']}",
        f"- CRIT alerts 24h: {metrics['budget']['crit_24h']}",
        f"- All alerts 7d:   {metrics['budget']['alerts_7d']}",
        "",
        "## 🚨 Escalations (V8.8 packets)",
        "",
        f"- Total escalations 24h: {metrics['escalations']['total_24h']}",
        f"- Total escalations 7d:  {metrics['escalations']['total_7d']}",
        f"- Rejected packets 24h:  {metrics['escalations']['rejected_packets_24h']}",
        f"- Rejection rate:        {_fmt_pct(metrics['escalations']['rejection_rate_pct'])}",
        "",
        "## 📐 Outcome rubric grading (V8.7 Clara)",
        "",
        f"- Graded 24h:  {metrics['outcomes']['graded_24h']}",
        f"- Passed 24h:  {metrics['outcomes']['passed_24h']}",
        f"- Returned 24h: {metrics['outcomes']['returned_24h']}",
        f"- Pass rate:   {_fmt_pct(metrics['outcomes']['pass_rate_pct'])}",
        "",
        "## 🔥 Maxwell override grading (V8.8 Cody)",
        "",
        f"- Graded 24h:               {metrics['maxwell_overrides']['graded_24h']}",
        f"- Passed 24h:               {metrics['maxwell_overrides']['passed_24h']}",
        f"- Escalated to Magnus 24h:  {metrics['maxwell_overrides']['escalated_to_magnus_24h']}",
        "",
        "## 🌐 Cross-agent learning (V8.8 Winston)",
        "",
        f"- Total lessons in `workspace/wiki/lessons_learned.md`: {metrics['cross_agent_learning']['lessons_total']:,}",
        f"- Multi-agent reinforced (count ≥ 2 agents):           {metrics['cross_agent_learning']['lessons_multi_agent_reinforced']:,}",
        "",
        "---",
        "",
        "**Methodology:** byte/4 token proxy; 24h/7d windows from now (UTC). Reads only the V8.6–V8.8 alert sinks listed in `scripts/metrics_summary.py`. Re-run every 15 min via cron after `install_metrics_cron.sh`.",
        "",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"metrics_summary: wrote {OUT_MD.relative_to(REPO_ROOT)}  + {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"  watch_list: {len(watch)} item(s)")
    return 0


def _rate(rejected: list[dict], total: list[dict], hours: int) -> float | None:
    r = sum(1 for x in rejected if within(x, hours))
    t = sum(1 for x in total if within(x, hours)) + r
    return round(100 * r / t, 1) if t else None


def _pass_rate(grades: list[dict], hours: int) -> float | None:
    rows = [g for g in grades if within(g, hours)]
    if not rows:
        return None
    passed = sum(1 for g in rows if g.get("decision") == "pass_to_cody")
    return round(100 * passed / len(rows), 1)


def _fmt_pct(v) -> str:
    return f"{v}%" if v is not None else "n/a (no data)"


if __name__ == "__main__":
    sys.exit(main())
