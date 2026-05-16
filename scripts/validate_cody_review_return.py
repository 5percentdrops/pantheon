#!/usr/bin/env python3
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

required = [
    "CODY_CODE_REVIEW_RETURN_FLOW.md",
    "UPDATED_CODY_MAGNUS_ESCALATION_CHAIN.md",
    "cody_review_return_policy.md",
    "CODY_CODE_REVIEW_RETURN_PACKET.template.md",
    "CODY_REVIEW_FAILED_PACKET.template.md",
    "cody_code_review_return.schema.json",
    "cody_review_return_routes.json",
]
for fname in required:
    if not any(p.name == fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")

agents = []
for p in ROOT.rglob("organization.import.json"):
    try:
        agents += json.loads(p.read_text(encoding="utf-8")).get("agents", [])
    except Exception:
        pass

roles = {a.get("role"): a for a in agents}
cody = roles.get("Code Escalation Reviewer", {})
if "security" not in (cody.get("description", "") + cody.get("skills", "")).lower():
    errors.append("Cody missing security review scope")
if "bug" not in (cody.get("description", "") + cody.get("skills", "")).lower():
    errors.append("Cody missing bug review scope")

route_files = list(ROOT.rglob("cody_review_return_routes.json"))
if route_files:
    text = json.dumps(json.loads(route_files[0].read_text(encoding="utf-8")))
    if "relevant-standard-engineer" not in text:
        errors.append("Cody route does not return to developer")
    if "magnus-principal-solution-architect" not in text:
        errors.append("Magnus route missing after Cody failure")
else:
    errors.append("missing cody route file")

if errors:
    print("CODY REVIEW RETURN VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("CODY REVIEW RETURN VALIDATION PASSED")
