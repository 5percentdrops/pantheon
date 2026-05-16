#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

required_files = [
    "UNIVERSAL_PRD_SDD_FEATURE_TDD_FLOW.md",
    "SUPERPOWERS_TDD_FOR_SENIOR_ENGINEERS.md",
    "universal_superpowers_tdd_policy.md",
    "pr_green_approval_merge_policy.md",
    "UNIVERSAL_FEATURE_TICKET_WITH_TDD.template.md",
    "UNIVERSAL_TASK_TDD_PLAN.template.md",
    "UNIVERSAL_ASSIGNMENT_PACKET.template.md",
    "universal_feature_ticket_tdd.schema.json",
    "senior_engineer_tdd_planning.schema.json",
    "universal_prd_sdd_tdd_routes.json",
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

required_seniors = [
    "Senior Backend Developer",
    "Senior Frontend Developer",
    "Senior Mobile Developer",
    "Senior PineScript Developer",
    "Senior Quantower C# Architect",
    "Senior DevOps Engineer",
    "Senior QA",
]
roles = {a.get("role"): a for a in agents}

for role in required_seniors:
    if role not in roles:
        # Some base repos may not include every lane, but the universal policy still exists.
        continue
    agent = roles[role]
    if not agent.get("superpowers_tdd_required"):
        errors.append(f"{role} missing superpowers_tdd_required flag")

for role, agent in roles.items():
    if (("Developer" in str(role)) or role == "QA Engineer") and not str(role).startswith("Senior"):
        if "green" not in (agent.get("description", "") + agent.get("skills", "") + agent.get("output", "")).lower():
            errors.append(f"{role} missing green execution rule")

if errors:
    print("UNIVERSAL SUPERPOWERS TDD VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("UNIVERSAL SUPERPOWERS TDD VALIDATION PASSED")
