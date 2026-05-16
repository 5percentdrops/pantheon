#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
errors=[]
required = [
 "OBSIDIAN_ERROR_MEMORY_PROTOCOL.md",
 "ERROR_MEMORY_FILE_NAMING.md",
 "obsidian_error_memory_policy.md",
 "error_memory_folder_purity_policy.md",
 "BLOCKER_LOG.template.md",
 "SOLUTION_LOG.template.md",
 "CODE_FIX_LOG.template.md",
 "APPROACH_SOLUTION_LOG.template.md",
 "obsidian_error_memory_log.schema.json",
 "obsidian_error_memory_routes.json"
]
for fname in required:
    if not any(p.name == fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")
agents=[]
for p in ROOT.rglob("organization.import.json"):
    try: agents += json.loads(p.read_text(encoding="utf-8")).get("agents",[])
    except Exception: pass
for name, write_type in [("Cody","code_fix_log"),("Magnus","approach_solution_log")]:
    matches=[a for a in agents if a.get("name")==name]
    if not matches:
        errors.append(f"missing {name}")
    elif matches[0].get("obsidian_error_memory_write_type") != write_type:
        errors.append(f"{name} missing write type {write_type}")
if not any(a.get("obsidian_error_memory_write_type")=="blocker_log" for a in agents):
    errors.append("no blocker_log writer")
if not any(a.get("obsidian_error_memory_write_type")=="solution_log" for a in agents):
    errors.append("no solution_log writer")
if errors:
    print("OBSIDIAN ERROR MEMORY VALIDATION FAILED")
    for e in errors: print("-", e)
    sys.exit(1)
print("OBSIDIAN ERROR MEMORY VALIDATION PASSED")
