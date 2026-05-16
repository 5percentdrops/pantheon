#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
errors=[]
for fname in ["ERROR_LEARNING_LOG_WORKFLOW.md","ERROR_LOG_EXAMPLE.md","error_learning_log_policy.md","wiki_error_memory_policy.md","ERROR_ESCALATION_PACKET.template.md","ERROR_LEARNING_LOG.template.md","error_learning_log.schema.json","error_learning_log_routes.json"]:
    if not any(p.name == fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")
if not any(str(p).endswith("wiki/errors/.gitkeep") for p in ROOT.rglob(".gitkeep")):
    errors.append("missing wiki/errors/.gitkeep")
agents=[]
for p in ROOT.rglob("organization.import.json"):
    try: agents += json.loads(p.read_text(encoding="utf-8")).get("agents",[])
    except Exception: pass
if not any(a.get("wiki_error_log_required") for a in agents):
    errors.append("no senior agents marked wiki_error_log_required")
if not any(a.get("error_escalation_packet_required") for a in agents):
    errors.append("no standard agents marked error_escalation_packet_required")
if errors:
    print("ERROR LEARNING LOG VALIDATION FAILED")
    for e in errors: print("-", e)
    sys.exit(1)
print("ERROR LEARNING LOG VALIDATION PASSED")
