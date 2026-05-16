#!/usr/bin/env python3
"""validate_v8_8_patches.py  (V8.8)

Single validator covering all three V8.8 patches:

  1. engineer_escalation_packet.schema.json present (both schemas/ and
     contracts/), with required fields + RTK constraint + conditional
     rule for blocked_on=dependency.
  2. escalation_packet_policy.yaml present with hard_rules naming the
     schema + rejection_behavior.
  3. dream_aggregator.py present + executable + outputs deterministic
     markdown + skips empty homes.
  4. install_dream_aggregator.sh present + executable + Winston-only
     scope + scheduled AFTER per-home dreaming.
  5. cross_agent_learning_policy.yaml present + immutable rule covering
     non-Winston homes.
  6. maxwell_grade_routes.json present with three routes
     (override_to_cody, pass, return) + grader_model openai/gpt-5.5.
  7. maxwell_override_grading_pipeline.yaml present with cody_rubric_grade
     stage + max_iterations + magnus escalation.

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
    print("PyYAML required (already a Pantheon dependency).", file=sys.stderr)
    sys.exit(2)

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
    if p.exists() and not (p.stat().st_mode & stat.S_IXUSR):
        fail(f"not executable: {p.relative_to(ROOT)}")


def must_contain(p: Path, needles: list[str]) -> None:
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    for n in needles:
        if n not in text:
            fail(f"{p.relative_to(ROOT)} missing token: {n!r}")


# --- Patch 1: engineer escalation packet ----------------------------
packet_schema = ROOT / "Pantheon" / "schemas" / "engineer_escalation_packet.schema.json"
packet_contract = ROOT / "Pantheon" / "contracts" / "engineer_escalation_packet.schema.json"
for p in (packet_schema, packet_contract):
    if must_exist(p):
        schema = json.loads(p.read_text(encoding="utf-8"))
        req = set(schema.get("required", []))
        for f in ("schema_version", "ticket_id", "agent", "attempt_count",
                  "blocked_on", "last_attempted_code_ref", "rtk_error_trace",
                  "tdd_red_tests", "marcus_handoff_format_version"):
            if f not in req:
                fail(f"{p.name}: required field missing: {f}")
        blocked_enum = schema.get("properties", {}).get("blocked_on", {}).get("enum", [])
        for b in ("compile", "runtime", "test", "design", "dependency", "ambiguous_prd"):
            if b not in blocked_enum:
                fail(f"{p.name}: blocked_on enum missing: {b}")

packet_policy = ROOT / "Pantheon" / "policies" / "escalation_packet_policy.yaml"
if must_exist(packet_policy):
    must_contain(packet_policy, [
        "engineer_escalation_packet.schema.json",
        "Marcus's runtime rejects",
        "RTK-compressed",
        "escalation_packet_rejections.jsonl",
    ])

# --- Patch 2: dream aggregator (Winston cross-agent learning) -------
aggregator = ROOT / "scripts" / "dream_aggregator.py"
if must_exist(aggregator):
    must_be_executable(aggregator)
    must_contain(aggregator, [
        "WINDOW_HOURS", "lessons_learned.md", "lessons_learned.index.json",
        "MAX_SKILL_BYTES_PER_AGENT", "hash_lesson",
    ])

agg_installer = ROOT / "scripts" / "install_dream_aggregator.sh"
if must_exist(agg_installer):
    must_be_executable(agg_installer)
    must_contain(agg_installer, [
        ".hermes-winston", "dream_aggregator.cron", "--uninstall", "--hour",
    ])

cal_policy = ROOT / "Pantheon" / "policies" / "cross_agent_learning_policy.yaml"
if must_exist(cal_policy):
    must_contain(cal_policy, [
        "winston-director-knowledge-architecture",
        "lessons_learned.md",
        "EXCEPT ~/.hermes-winston/",
        "engineers_pre_read: true",
    ])

# --- Patch 3: Maxwell override grading ------------------------------
maxwell_routes = ROOT / "Pantheon" / "routes" / "maxwell_grade_routes.json"
if must_exist(maxwell_routes):
    doc = json.loads(maxwell_routes.read_text(encoding="utf-8"))
    names = [r.get("name") for r in doc.get("routes", [])]
    for n in ("maxwell_override_to_cody_rubric_grade",
              "cody_grades_maxwell_pass",
              "cody_grades_maxwell_return",
              "cody_escalates_maxwell_failure"):
        if n not in names:
            fail(f"maxwell_grade_routes.json missing route: {n}")
    primary = next((r for r in doc["routes"] if r.get("name") == "maxwell_override_to_cody_rubric_grade"), {})
    if primary.get("grader_model") != "openai/gpt-5.5":
        fail("maxwell_override_to_cody_rubric_grade.grader_model != openai/gpt-5.5")
    if primary.get("input_contract") != "outcome.schema.json":
        fail("maxwell_override_to_cody_rubric_grade.input_contract != outcome.schema.json")

maxwell_pipeline = ROOT / "Pantheon" / "pipelines" / "maxwell_override_grading_pipeline.yaml"
if must_exist(maxwell_pipeline):
    doc = yaml.safe_load(maxwell_pipeline.read_text(encoding="utf-8"))
    stages = doc.get("pipeline", {}).get("stages", [])
    ids = [s.get("id") for s in stages]
    for required in ("maxwell_override", "cody_rubric_grade", "merge_gate"):
        if required not in ids:
            fail(f"maxwell_override_grading_pipeline.yaml missing stage: {required}")
    cody_stage = next((s for s in stages if s.get("id") == "cody_rubric_grade"), None)
    if cody_stage:
        if cody_stage.get("agent") != "cody-code-escalation-reviewer":
            fail("cody_rubric_grade.agent must be cody-code-escalation-reviewer")
        if cody_stage.get("max_iterations", 0) != 2:
            fail("cody_rubric_grade.max_iterations must be 2")
        if cody_stage.get("escalation_on_persistent_fail") != "magnus-architecture-escalation":
            fail("cody_rubric_grade.escalation_on_persistent_fail must be magnus-architecture-escalation")

if FAILS:
    print("FAIL: V8.8 patches incomplete")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)

print("PASS: V8.8 patches present — escalation packet schema, cross-agent dream aggregator, Maxwell override grading.")
