#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

required_files = [
    "PRD_TO_SDD_TICKET_TDD_PIPELINE.md",
    "USER_APPROVAL_GATE.md",
    "green_before_next_task_policy.md",
    "prd_approval_policy.md",
    "marcus_tdd_planning_policy.md",
    "SDD.template.md",
    "FEATURE_TICKET.template.md",
    "TASK_TDD_PLAN.template.md",
    "JACK_ASSIGNMENT_PACKET.template.md",
    "prd_to_sdd_pipeline.schema.json",
    "task_tdd_block.schema.json",
    "user_approval_gate.schema.json",
    "prd_delivery_and_approval_routes.json",
    "marcus_to_jack_task_routes.json",
]

for fname in required_files:
    if not any(p.name == fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")

agents = []
for p in ROOT.rglob("organization.import.json"):
    try:
        agents.extend(json.loads(p.read_text(encoding="utf-8")).get("agents", []))
    except Exception:
        pass
roles = {a.get("role"): a for a in agents}

for role in ["Project Manager", "Senior Backend Developer", "Backend Developer"]:
    if role not in roles:
        errors.append(f"missing role: {role}")

marcus = roles.get("Senior Backend Developer", {})
for required_text in ["SDD", "feature", "TDD"]:
    if required_text.lower() not in (marcus.get("description", "") + marcus.get("skills", "")).lower():
        errors.append(f"Marcus missing responsibility: {required_text}")

if errors:
    print("PRD/SDD/TDD PIPELINE VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("PRD/SDD/TDD PIPELINE VALIDATION PASSED")
