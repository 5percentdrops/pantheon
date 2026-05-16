#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
required_files = [
    "UNIVERSAL_ENGINEERING_ESCALATION.md",
    "ENGINEERING_LANE_MAP.md",
    "universal_engineering_escalation_policy.md",
    "universal_engineering_escalation_routes.json",
    "universal_engineering_escalation.schema.json",
    "UNIVERSAL_BLOCKER_PACKET.template.md",
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
for role in ["Project Manager", "Code Escalation Reviewer", "Principal Solution Architect"]:
    if role not in roles:
        errors.append(f"missing universal role: {role}")
for p in ROOT.rglob("universal_engineering_escalation_routes.json"):
    data = json.loads(p.read_text(encoding="utf-8"))
    text = json.dumps(data)
    for required in ["arthur-project-manager", "cody-code-escalation-reviewer", "magnus-principal-solution-architect"]:
        if required not in text:
            errors.append(f"universal route missing {required}")
if errors:
    print("UNIVERSAL ENGINEERING ESCALATION VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("UNIVERSAL ENGINEERING ESCALATION VALIDATION PASSED")
