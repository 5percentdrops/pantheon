#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
errors=[]
required=["ERROR_MEMORY_LOGGING_OWNERSHIP.md","error_memory_logging_ownership_policy.md","LOGGING_OWNERSHIP_CHECKLIST.template.md","error_memory_logging_ownership_routes.json","error_memory_logging_ownership.schema.json"]
for fname in required:
    if not any(p.name==fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")
agents=[]
for p in ROOT.rglob("organization.import.json"):
    try: agents += json.loads(p.read_text(encoding="utf-8")).get("agents",[])
    except Exception: pass
for a in agents:
    if a.get("harness") != "Hermes":
        errors.append(f"non-Hermes harness: {a.get('name')}={a.get('harness')}")
by={a.get("name"):a for a in agents}
for name in ["Jack","Marcus","Maxwell","Cody","Magnus","Arthur"]:
    if not by.get(name,{}).get("error_memory_logging_role"):
        errors.append(f"{name} missing logging role")
if errors:
    print("FINAL LOGGING OWNERSHIP VALIDATION FAILED")
    for e in errors: print("-",e)
    sys.exit(1)
print("FINAL LOGGING OWNERSHIP VALIDATION PASSED")
