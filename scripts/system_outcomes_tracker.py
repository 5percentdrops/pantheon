#!/usr/bin/env python3
"""system_outcomes_tracker.py  (V8.9) — Org-wide weekly scorecard

Per-ticket outcomes (V8.7) grade individual implementations.
THIS file grades the COMPANY.

Reads the V8.9 metrics_dashboard.json and the V8.7-V8.8 audit logs,
evaluates against system_outcomes.schema.json defaults, writes:

  workspace/07_Finalization/system_outcomes_weekly.json
  workspace/07_Finalization/system_outcomes_weekly.md

Verdict logic:
  - 0 failed criteria  -> healthy
  - 1-2 failed         -> watch
  - 3+ failed          -> escalate_to_board

When verdict == escalate_to_board, an entry is appended to
Arthur's MEMORY.md so the human board sees it on next dispatch.

Pure file IO. No LLM. Cron weekly (Mon 06:00 UTC) via Winston home.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = REPO_ROOT / "workspace"
FIN_DIR = WORKSPACE / "07_Finalization"
AUDIT_DIR = WORKSPACE / "05_QA_Audit_Logs"
ARTHUR_MEMORY = Path.home() / ".hermes-arthur" / "MEMORY.md"

OUT_JSON = FIN_DIR / "system_outcomes_weekly.json"
OUT_MD = FIN_DIR / "system_outcomes_weekly.md"

WINDOW_DAYS = 7

# Defaults match the V8.9 system_outcomes.schema.json
TARGET_PIPELINE_COMPLETION_PCT = 90
TARGET_MAX_AVG_ITERATIONS = 2.0
TARGET_MAX_ESCALATION_RATE_PCT = 15
TARGET_MAX_CRIT_ALERTS_WEEK = 0
TARGET_MIN_MULTI_AGENT_LESSONS_PCT = 20


def read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def within_week(row: dict, key: str = "timestamp_utc") -> bool:
    ts = parse_iso(row.get(key))
    if not ts:
        return False
    return ts >= datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)


def main() -> int:
    if not WORKSPACE.exists():
        print(f"system_outcomes: {WORKSPACE} missing — run installer first.", file=sys.stderr)
        return 1
    FIN_DIR.mkdir(parents=True, exist_ok=True)

    outcomes = read_jsonl(AUDIT_DIR / "outcome_grades.jsonl")
    escalations = read_jsonl(AUDIT_DIR / "escalation_packets.jsonl")
    rejections = read_jsonl(AUDIT_DIR / "escalation_packet_rejections.jsonl")
    maxwell = read_jsonl(AUDIT_DIR / "maxwell_override_grades.jsonl")
    budget = read_jsonl(FIN_DIR / "budget_alerts.jsonl")

    # Pipeline completion: tickets graded as pass_to_cody / total graded
    outcomes_week = [r for r in outcomes if within_week(r)]
    tickets_attempted = len(outcomes_week)
    tickets_merged = sum(1 for r in outcomes_week if r.get("decision") == "pass_to_cody")
    actual_pipeline_pct = round(100 * tickets_merged / tickets_attempted, 1) if tickets_attempted else 0
    pipeline_passed = (tickets_attempted == 0) or actual_pipeline_pct >= TARGET_PIPELINE_COMPLETION_PCT

    # Iteration efficiency: avg `iteration` field across graded outcomes
    iters = [r.get("iteration") for r in outcomes_week if isinstance(r.get("iteration"), (int, float))]
    actual_avg_iter = round(sum(iters) / len(iters), 2) if iters else 1.0
    iter_passed = actual_avg_iter <= TARGET_MAX_AVG_ITERATIONS

    # Escalation health
    esc_week = [r for r in escalations if within_week(r)]
    rej_week = [r for r in rejections if within_week(r)]
    actual_esc_rate = round(100 * len(esc_week) / max(tickets_attempted, 1), 1)
    rej_rate = round(100 * len(rej_week) / max(len(esc_week) + len(rej_week), 1), 1)
    mw_week = [r for r in maxwell if within_week(r)]
    mw_rate = round(100 * len(mw_week) / max(tickets_attempted, 1), 1)
    esc_passed = actual_esc_rate <= TARGET_MAX_ESCALATION_RATE_PCT

    # Budget health
    crit_week = sum(1 for r in budget if within_week(r) and r.get("severity") == "CRIT")
    warn_week = sum(1 for r in budget if within_week(r) and r.get("severity") == "WARN")
    budget_passed = crit_week <= TARGET_MAX_CRIT_ALERTS_WEEK

    # Learning compounding
    lessons_path = WORKSPACE / "wiki" / "lessons_learned.index.json"
    lessons_total = 0
    lessons_reinforced = 0
    if lessons_path.exists():
        try:
            d = json.loads(lessons_path.read_text(encoding="utf-8"))
            lessons_total = len(d)
            lessons_reinforced = sum(1 for v in d.values() if len(v.get("agents", [])) > 1)
        except (json.JSONDecodeError, OSError):
            pass
    reinforced_pct = round(100 * lessons_reinforced / max(lessons_total, 1), 1)
    learning_passed = (lessons_total == 0) or reinforced_pct >= TARGET_MIN_MULTI_AGENT_LESSONS_PCT

    failed = []
    if not pipeline_passed: failed.append(f"pipeline_completion {actual_pipeline_pct}% < {TARGET_PIPELINE_COMPLETION_PCT}%")
    if not iter_passed: failed.append(f"avg_iterations {actual_avg_iter} > {TARGET_MAX_AVG_ITERATIONS}")
    if not esc_passed: failed.append(f"escalation_rate {actual_esc_rate}% > {TARGET_MAX_ESCALATION_RATE_PCT}%")
    if not budget_passed: failed.append(f"crit_budget_alerts {crit_week} > {TARGET_MAX_CRIT_ALERTS_WEEK}")
    if not learning_passed: failed.append(f"multi_agent_lessons_pct {reinforced_pct}% < {TARGET_MIN_MULTI_AGENT_LESSONS_PCT}%")

    if len(failed) == 0:
        verdict = "healthy"
    elif len(failed) <= 2:
        verdict = "watch"
    else:
        verdict = "escalate_to_board"

    snapshot = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "schema_version": "system_outcomes.v1",
        "snapshot_utc": snapshot,
        "window_days": WINDOW_DAYS,
        "pipeline_completion": {
            "target_pct": TARGET_PIPELINE_COMPLETION_PCT,
            "actual_pct": actual_pipeline_pct,
            "tickets_attempted": tickets_attempted,
            "tickets_merged": tickets_merged,
            "passed": pipeline_passed,
        },
        "iteration_efficiency": {
            "target_max_avg_iterations": TARGET_MAX_AVG_ITERATIONS,
            "actual_avg_iterations": actual_avg_iter,
            "passed": iter_passed,
        },
        "escalation_health": {
            "target_max_escalation_rate_pct": TARGET_MAX_ESCALATION_RATE_PCT,
            "actual_escalation_rate_pct": actual_esc_rate,
            "packet_rejection_rate_pct": rej_rate,
            "maxwell_override_rate_pct": mw_rate,
            "passed": esc_passed,
        },
        "budget_health": {
            "target_max_crit_alerts_week": TARGET_MAX_CRIT_ALERTS_WEEK,
            "actual_crit_alerts_week": crit_week,
            "warn_alerts_week": warn_week,
            "passed": budget_passed,
        },
        "learning_compounding": {
            "target_min_multi_agent_lessons_pct": TARGET_MIN_MULTI_AGENT_LESSONS_PCT,
            "actual_multi_agent_lessons_pct": reinforced_pct,
            "lessons_total": lessons_total,
            "lessons_reinforced": lessons_reinforced,
            "passed": learning_passed,
        },
        "verdict": verdict,
        "failed_criteria": failed,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    icon = {"healthy": "✅", "watch": "🟡", "escalate_to_board": "🔴"}[verdict]
    md = [
        f"# Pantheon — Weekly System Outcomes ({snapshot})",
        "",
        f"## Verdict: {icon} **{verdict.upper().replace('_', ' ')}**",
        "",
        f"Window: last {WINDOW_DAYS} days.",
        "",
        "| Criterion | Target | Actual | Pass |",
        "|---|---|---|---|",
        f"| Pipeline completion | ≥ {TARGET_PIPELINE_COMPLETION_PCT}% | {actual_pipeline_pct}% ({tickets_merged}/{tickets_attempted}) | {'✅' if pipeline_passed else '❌'} |",
        f"| Avg iterations per ticket | ≤ {TARGET_MAX_AVG_ITERATIONS} | {actual_avg_iter} | {'✅' if iter_passed else '❌'} |",
        f"| Escalation rate | ≤ {TARGET_MAX_ESCALATION_RATE_PCT}% | {actual_esc_rate}% | {'✅' if esc_passed else '❌'} |",
        f"| Packet rejection rate | < 25% (informational) | {rej_rate}% | — |",
        f"| Maxwell override rate | < 5% (informational) | {mw_rate}% | — |",
        f"| CRIT budget alerts | ≤ {TARGET_MAX_CRIT_ALERTS_WEEK} | {crit_week} | {'✅' if budget_passed else '❌'} |",
        f"| Multi-agent lesson share | ≥ {TARGET_MIN_MULTI_AGENT_LESSONS_PCT}% | {reinforced_pct}% ({lessons_reinforced}/{lessons_total}) | {'✅' if learning_passed else '❌'} |",
        "",
    ]
    if failed:
        md += ["## Failed criteria", ""] + [f"- {f}" for f in failed] + [""]

    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    if verdict == "escalate_to_board" and ARTHUR_MEMORY.exists():
        try:
            with ARTHUR_MEMORY.open("a", encoding="utf-8") as f:
                f.write(
                    f"\n## V8.9 system outcomes ESCALATE_TO_BOARD {snapshot}\n"
                    f"- Failed criteria ({len(failed)}): " + "; ".join(failed) + "\n"
                    f"- Full report: workspace/07_Finalization/system_outcomes_weekly.md\n"
                )
        except OSError:
            pass

    print(f"system_outcomes_tracker: verdict={verdict}, failed={len(failed)}, "
          f"wrote {OUT_MD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
