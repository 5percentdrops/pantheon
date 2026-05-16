#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
required_roles = [
    "PineScript Developer",
    "Senior PineScript Developer",
    "Quantower C# Automation Developer",
    "Senior Quantower C# Architect",
    "Project Manager",
]
agents = []
for p in ROOT.rglob("organization.import.json"):
    try:
        agents.extend(json.loads(p.read_text(encoding="utf-8")).get("agents", []))
    except Exception:
        pass
roles = {a.get("role") for a in agents}
for role in required_roles:
    if role not in roles:
        errors.append(f"missing role: {role}")

required_files = [
    "TECHNICAL_DOMAIN_ROUTING.md",
    "arthur_technical_domain_routing_policy.md",
    "technical_domain_routes.json",
    "technical_domain_routing_decision.schema.json",
]
for fname in required_files:
    if not any(p.name == fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")

if errors:
    print("TECHNICAL DOMAIN ROUTING VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("TECHNICAL DOMAIN ROUTING VALIDATION PASSED")
