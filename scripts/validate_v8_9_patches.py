#!/usr/bin/env python3
"""validate_v8_9_patches.py  (V8.9)

Verifies the V8.9 observability layer ships intact:

  1. metrics_summary.py            present, executable, refs all V8.6-V8.8 sinks
  2. install_metrics_cron.sh       present, executable, Arthur-only scope
  3. system_outcomes.schema.json   present in schemas/ AND contracts/, has
                                   verdict enum + 5 criteria objects
  4. system_outcomes_tracker.py    present, executable, writes both
                                   .json + .md outputs
  5. redundant_work_detector.py    present, executable, scans agents.json
  6. install_observability_crons.sh   present, executable, installs all 3
  7. observability_pipeline.yaml   present, declares 3 stages + no_llm
                                   invariant
  8. observability_policy.yaml     present, lists inputs + thresholds
  9. Stub run of each script does not raise (smoke-level)

Exits 0 on pass, 1 on any failure.
"""
from __future__ import annotations
import json
import stat
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required.", file=sys.stderr); sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
FAILS: list[str] = []

def fail(m: str): FAILS.append(m)
def must_exist(p: Path) -> bool:
    if not p.exists(): fail(f"missing: {p.relative_to(ROOT)}"); return False
    return True
def must_exec(p: Path):
    if p.exists() and not (p.stat().st_mode & stat.S_IXUSR):
        fail(f"not executable: {p.relative_to(ROOT)}")
def must_contain(p: Path, needles: list[str]):
    if not p.exists(): return
    text = p.read_text(encoding="utf-8")
    for n in needles:
        if n not in text:
            fail(f"{p.relative_to(ROOT)} missing token: {n!r}")

# --- 1. metrics_summary.py
metrics = ROOT / "scripts" / "metrics_summary.py"
if must_exist(metrics):
    must_exec(metrics)
    must_contain(metrics, [
        "budget_alerts.jsonl",
        "escalation_packet_rejections.jsonl",
        "outcome_grades.jsonl",
        "maxwell_override_grades.jsonl",
        "lessons_learned.index.json",
        "metrics_dashboard.md",
        "metrics_dashboard.json",
        "watch_list",
    ])

# --- 2. install_metrics_cron.sh
mcron = ROOT / "scripts" / "install_metrics_cron.sh"
if must_exist(mcron):
    must_exec(mcron)
    must_contain(mcron, [".hermes-arthur", "metrics_summary.cron", "--uninstall"])

# --- 3. system_outcomes schema in schemas/ AND contracts/
for loc in (("Pantheon/schemas",), ("Pantheon/contracts",)):
    p = ROOT / loc[0] / "system_outcomes.schema.json"
    if must_exist(p):
        s = json.loads(p.read_text(encoding="utf-8"))
        for f in ("schema_version", "verdict", "pipeline_completion",
                  "iteration_efficiency", "escalation_health", "budget_health",
                  "learning_compounding"):
            if f not in set(s.get("required", [])):
                fail(f"{loc[0]}/system_outcomes.schema.json: required missing: {f}")
        verdict_enum = s.get("properties", {}).get("verdict", {}).get("enum", [])
        for v in ("healthy", "watch", "escalate_to_board"):
            if v not in verdict_enum:
                fail(f"{loc[0]}/system_outcomes.schema.json: verdict enum missing: {v}")

# --- 4. system_outcomes_tracker.py
tracker = ROOT / "scripts" / "system_outcomes_tracker.py"
if must_exist(tracker):
    must_exec(tracker)
    must_contain(tracker, [
        "system_outcomes_weekly.json",
        "system_outcomes_weekly.md",
        "escalate_to_board",
        "TARGET_PIPELINE_COMPLETION_PCT",
        "ARTHUR_MEMORY",
    ])

# --- 5. redundant_work_detector.py
red = ROOT / "scripts" / "redundant_work_detector.py"
if must_exist(red):
    must_exec(red)
    must_contain(red, [
        "agents.json",
        "redundant_work_report.md",
        "JACCARD_THRESHOLD",
        "seed_skill_path",
        "consumes_from",
        "produces_for",
    ])

# --- 6. install_observability_crons.sh
ocron = ROOT / "scripts" / "install_observability_crons.sh"
if must_exist(ocron):
    must_exec(ocron)
    must_contain(ocron, [
        "metrics_summary.cron",
        "system_outcomes_weekly.cron",
        "redundant_work_weekly.cron",
        ".hermes-arthur",
        ".hermes-winston",
    ])

# --- 7. observability_pipeline.yaml
pipeline = ROOT / "Pantheon" / "pipelines" / "observability_pipeline.yaml"
if must_exist(pipeline):
    doc = yaml.safe_load(pipeline.read_text(encoding="utf-8"))
    stages = doc.get("pipeline", {}).get("stages", [])
    ids = [s.get("id") for s in stages]
    for need in ("metrics_rollup", "system_outcomes_weekly", "redundant_work_weekly"):
        if need not in ids: fail(f"observability_pipeline.yaml missing stage: {need}")
    must_contain(pipeline, ["observability_never_calls_llm"])

# --- 8. observability_policy.yaml
policy = ROOT / "Pantheon" / "policies" / "observability_policy.yaml"
if must_exist(policy):
    must_contain(policy, [
        "metrics_summary",
        "system_outcomes",
        "redundant_work",
        "Observability scripts NEVER call an LLM",
        "redundant_work_jaccard_threshold",
    ])

# --- 9. Smoke runs
if not FAILS:
    for script in (metrics, tracker, red):
        try:
            r = subprocess.run([sys.executable, str(script)],
                               capture_output=True, text=True, timeout=20)
            if r.returncode != 0:
                fail(f"{script.name} smoke-run exited {r.returncode}: {r.stderr.strip()[:200]}")
        except Exception as e:
            fail(f"{script.name} smoke-run raised: {e}")

if FAILS:
    print("FAIL: V8.9 patches incomplete")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)

print("PASS: V8.9 observability layer wired — metrics dashboard + system outcomes + redundant work detector.")
