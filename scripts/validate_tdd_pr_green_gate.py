#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

required_files = [
    "task_tdd_and_pr_green_gate_policy.md",
    "TDD_SEQUENTIAL_EXECUTION_AND_PR_MERGE_GATE.md",
    "tdd_task_and_pr_gate_routes.json",
    "TASK_TDD_PLAN.template.md",
    "JACK_ASSIGNMENT_PACKET.template.md",
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
for role in ["Backend Developer", "Senior Backend Developer", "PineScript Developer", "Senior PineScript Developer"]:
    if role not in roles:
        errors.append(f"missing role: {role}")

jack = roles.get("Backend Developer", {})
jack_text = (jack.get("description", "") + " " + jack.get("skills", "") + " " + jack.get("output", "")).lower()
for phrase in ["green", "approved", "merge"]:
    if phrase not in jack_text:
        errors.append(f"Jack missing {phrase} responsibility")

if errors:
    print("TDD/PR GREEN GATE VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("TDD/PR GREEN GATE VALIDATION PASSED")
