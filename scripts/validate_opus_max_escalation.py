#!/usr/bin/env python3
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

required_files = [
    "OPUS_MAX_ESCALATION_LAYER.md",
    "UPDATED_UNIVERSAL_ESCALATION_CHAIN.md",
    "opus_max_escalation_policy.md",
    "OPUS_MAX_ESCALATION_REPORT.template.md",
    "opus_max_escalation.schema.json",
    "opus_max_escalation_routes.json",
]
for fname in required_files:
    if not any(p.name == fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")

agents = []
for p in ROOT.rglob("organization.import.json"):
    try:
        agents += json.loads(p.read_text(encoding="utf-8")).get("agents", [])
    except Exception:
        pass

if not any(a.get("id") == "maxwell-opus-max-escalation-engineer" for a in agents):
    errors.append("missing Maxwell Opus Max Escalation Engineer")

maxwell = next((a for a in agents if a.get("id") == "maxwell-opus-max-escalation-engineer"), {})
if "Opus 4.7 Max" not in maxwell.get("llm_module", "") and "OPS / Opus 4.7 Max" not in maxwell.get("llm_module", ""):
    errors.append("Maxwell model assignment missing Opus 4.7 Max")

route_files = list(ROOT.rglob("opus_max_escalation_routes.json"))
if route_files:
    text = json.dumps(json.loads(route_files[0].read_text(encoding="utf-8")))
    for required in [
        "maxwell-opus-max-escalation-engineer",
        "cody-code-escalation-reviewer",
        "magnus-principal-solution-architect"
    ]:
        if required not in text:
            errors.append(f"route missing {required}")
else:
    errors.append("missing opus max route file")

if errors:
    print("OPUS MAX ESCALATION VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("OPUS MAX ESCALATION VALIDATION PASSED")
