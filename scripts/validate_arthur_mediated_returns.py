#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
errors=[]
required=[
 "ARTHUR_MEDIATED_RETURN_ROUTING.md",
 "FINAL_ESCALATION_CHAIN_WITH_ARTHUR.md",
 "arthur_mediated_return_policy.md",
 "arthur_mediated_return_routes.json",
 "arthur_mediated_return.schema.json",
 "ARTHUR_MEDIATED_RETURN_PACKET.template.md"
]
for fname in required:
    if not any(p.name==fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")
agents=[]
for p in ROOT.rglob("organization.import.json"):
    try: agents += json.loads(p.read_text(encoding="utf-8")).get("agents",[])
    except Exception: pass
for name in ["Marcus","Maxwell","Cody","Magnus"]:
    matches=[a for a in agents if a.get("name")==name]
    if not matches:
        errors.append(f"missing {name}")
    elif not matches[0].get("arthur_mediated_return_required"):
        errors.append(f"{name} missing arthur_mediated_return_required")
route_files=list(ROOT.rglob("arthur_mediated_return_routes.json"))
if route_files:
    text=json.dumps(json.loads(route_files[0].read_text(encoding="utf-8")))
    for token in ["arthur-project-manager","jack-backend-developer","marcus-senior-backend-developer","maxwell-opus-max-escalation-engineer","cody-code-escalation-reviewer","magnus-principal-solution-architect"]:
        if token not in text:
            errors.append(f"route missing {token}")
else:
    errors.append("missing route file")
if errors:
    print("ARTHUR MEDIATED RETURNS VALIDATION FAILED")
    for e in errors: print("-",e)
    sys.exit(1)
print("ARTHUR MEDIATED RETURNS VALIDATION PASSED")
