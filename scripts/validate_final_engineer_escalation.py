#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
errors=[]
required_files=[
 "FINAL_ENGINEER_ESCALATION_ROUTINE.md",
 "ENGINEER_AGENT_SPECIFICATIONS.md",
 "final_engineer_escalation_policy.md",
 "final_engineer_escalation_routes.json",
 "final_engineer_escalation.schema.json",
 "FINAL_ESCALATION_STATUS.template.md"
]
for fname in required_files:
    if not any(p.name==fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")
agents=[]
for p in ROOT.rglob("organization.import.json"):
    try: agents += json.loads(p.read_text(encoding="utf-8")).get("agents",[])
    except Exception: pass
by_name={a.get("name"):a for a in agents}
checks = {
 "Jack": ("self_fix_attempt_budget", 15),
 "Marcus": ("solution_attempt_budget", 3),
 "Maxwell": ("solution_attempt_budget", 2),
 "Cody": ("review_pass_budget", 1)
}
for name,(field,value) in checks.items():
    a=by_name.get(name,{})
    if a.get(field)!=value:
        errors.append(f"{name} missing {field}={value}")
if by_name.get("Cody",{}).get("role")!="Senior Code Quality & Defect Review Engineer":
    errors.append("Cody title not finalized")
if by_name.get("Maxwell",{}).get("role")!="Staff Escalation Engineer":
    errors.append("Maxwell title not finalized")
routes=list(ROOT.rglob("final_engineer_escalation_routes.json"))
if routes:
    text=json.dumps(json.loads(routes[0].read_text(encoding="utf-8")))
    for token in ["jack-backend-developer","marcus-senior-backend-developer","maxwell-opus-max-escalation-engineer","cody-code-escalation-reviewer","magnus-principal-solution-architect"]:
        if token not in text:
            errors.append(f"route missing {token}")
else:
    errors.append("missing route file")
if errors:
    print("FINAL ENGINEER ESCALATION VALIDATION FAILED")
    for e in errors: print("-",e)
    sys.exit(1)
print("FINAL ENGINEER ESCALATION VALIDATION PASSED")
