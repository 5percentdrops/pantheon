#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
errors = []
required = {
 "Project Manager":"OPS 4.7",
 "Backend Developer":"OPS 4.7 High",
 "Senior Backend Developer":"OPS 4.7 Extra High",
 "Code Escalation Reviewer":"GPT-5.5",
 "Principal Solution Architect":"Gemini Pro"
}
agents=[]
for p in ROOT.rglob("organization.import.json"):
    try: agents += json.loads(p.read_text()).get("agents", [])
    except Exception: pass
roles={a.get("role"):a for a in agents}
for role, model in required.items():
    if role not in roles: errors.append(f"missing role {role}")
    elif model not in roles[role].get("llm_module",""): errors.append(f"model mismatch {role}")
for p in ROOT.rglob("software_house_escalation_routes.json"):
    route=json.loads(p.read_text())["routes"][0]["path"]
    for i in range(len(route)-1):
        if route[i]=="magnus-principal-solution-architect" and route[i+1]=="jack-backend-developer":
            errors.append("Magnus routes directly to Jack")
if errors:
    print("PARALLEL ESCALATION VALIDATION FAILED")
    print("\n".join(errors))
    sys.exit(1)
print("PARALLEL ESCALATION VALIDATION PASSED")
