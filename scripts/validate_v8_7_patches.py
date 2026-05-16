#!/usr/bin/env python3
"""validate_v8_7_patches.py  (V8.7)

Single validator covering all four V8.7 patches:

  - Outcome rubric schema + grade schema present, with required fields
  - outcome_grading_policy.yaml present + rubric_required: true
  - parallel_dispatch_policy.yaml present + engineers_pool >=4
  - budget_watcher.py present + executable + has alert thresholds
  - install_budget_watcher.sh present + executable + Arthur-only scope
  - claude_managed_burst.yaml present + status declares stub
  - claude_managed_burst_adapter.py present + returns burst_unavailable
    when no real endpoint configured

Exits 0 on pass, 1 on any failure.
"""
from __future__ import annotations
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILS: list[str] = []


def fail(msg: str) -> None:
    FAILS.append(msg)


def must_exist(p: Path) -> bool:
    if not p.exists():
        fail(f"missing: {p.relative_to(ROOT)}")
        return False
    return True


def must_be_executable(p: Path) -> None:
    if not p.exists():
        return
    if not (p.stat().st_mode & stat.S_IXUSR):
        fail(f"not executable: {p.relative_to(ROOT)}")


def must_contain(p: Path, needles: list[str]) -> None:
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    for n in needles:
        if n not in text:
            fail(f"{p.relative_to(ROOT)} missing token: {n!r}")


# --- Outcome rubric ---------------------------------------------------
rubric = ROOT / "Pantheon" / "schemas" / "outcome.schema.json"
if must_exist(rubric):
    schema = json.loads(rubric.read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    for f in ("ticket_id", "must_have", "rubric_score_min", "grader", "max_iterations"):
        if f not in required:
            fail(f"outcome.schema.json: required field missing: {f}")

grade = ROOT / "Pantheon" / "schemas" / "outcome_grade.schema.json"
if must_exist(grade):
    schema = json.loads(grade.read_text(encoding="utf-8"))
    decisions = schema.get("properties", {}).get("decision", {}).get("enum", [])
    for d in ("pass_to_cody", "return_to_jack", "escalate"):
        if d not in decisions:
            fail(f"outcome_grade.schema.json: decision enum missing: {d}")

policy = ROOT / "Pantheon" / "policies" / "outcome_grading_policy.yaml"
if must_exist(policy):
    must_contain(policy, ["rubric_required: true", "clara-claude-pr-review-lead"])

# --- Parallel dispatch ------------------------------------------------
fanout = ROOT / "Pantheon" / "policies" / "parallel_dispatch_policy.yaml"
if must_exist(fanout):
    text = fanout.read_text(encoding="utf-8")
    must_contain(fanout, [
        "engineers_pool",
        "max_parallel_lanes",
        "depends_on == []",
        "Serial fallback",
    ])
    # Confirm pool has at least 4 engineers
    pool_count = sum(1 for line in text.splitlines() if line.strip().startswith("- ") and "-engineer" in line or "developer" in line)
    if pool_count < 4:
        fail(f"parallel_dispatch_policy.yaml: engineers_pool has only {pool_count} entries (expected >=4)")

# --- Budget watcher ---------------------------------------------------
watcher = ROOT / "scripts" / "budget_watcher.py"
if must_exist(watcher):
    must_be_executable(watcher)
    must_contain(watcher, ["THRESHOLD_WARN", "THRESHOLD_CRIT", "budget_alerts.jsonl", "ARTHUR_MEMORY"])

bw_installer = ROOT / "scripts" / "install_budget_watcher.sh"
if must_exist(bw_installer):
    must_be_executable(bw_installer)
    must_contain(bw_installer, ["budget_watcher.cron", ".hermes-arthur", "--uninstall", "--interval"])

# --- Claude MA burst lane --------------------------------------------
burst_spec = ROOT / "Pantheon" / "harnesses" / "claude_managed_burst.yaml"
if must_exist(burst_spec):
    must_contain(burst_spec, [
        "type: claude_managed_agents",
        "identity_layer_unchanged: hermes_local",
        "max_children: 5",
        "fallback_if_disabled: marcus_sequential_decomposition",
        "status:",
        "shipped: spec_only",
    ])

burst_adapter = ROOT / "scripts" / "claude_managed_burst_adapter.py"
if must_exist(burst_adapter):
    must_be_executable(burst_adapter)
    # Behavioral check: with no subsystems, returns burst_error;
    # with >=2 subsystems, returns burst_unavailable (stub fallback).
    try:
        payload = json.dumps({"subsystems": ["a", "b", "c"]})
        result = subprocess.run(
            [sys.executable, str(burst_adapter)],
            input=payload, capture_output=True, text=True, timeout=10,
        )
        out = json.loads(result.stdout)
        if out.get("status") != "burst_unavailable":
            fail(f"claude_managed_burst_adapter.py: expected status=burst_unavailable, got {out.get('status')!r}")
        if out.get("fallback") != "marcus_sequential_decomposition":
            fail("claude_managed_burst_adapter.py: fallback path not declared")
    except Exception as e:
        fail(f"claude_managed_burst_adapter.py: stdin invocation failed: {e}")

# --- SMOKE_SCALE.md ---------------------------------------------------
smoke = ROOT / "SMOKE_SCALE.md"
if must_exist(smoke):
    must_contain(smoke, ["Phase 1: Triad", "Phase 6: Full pantheon", "Owen excluded"])

if FAILS:
    print("FAIL: V8.7 patches incomplete")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)

print("PASS: V8.7 patches present — outcome rubric, fan-out policy, budget watcher, Claude MA burst spec, smoke ramp doc.")
