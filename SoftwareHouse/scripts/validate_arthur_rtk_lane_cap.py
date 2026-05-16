#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
errors = []
required = [
 "ARTHUR_RTK_SQUASHED_ROUTING.md",
 "LANE_CONCURRENCY_LIMIT.md",
 "UPDATED_ARTHUR_MODEL.md",
 "arthur_rtk_squash_policy.md",
 "lane_concurrency_policy.md",
 "arthur_rtk_lane_routes.json",
 "arthur_rtk_routing_packet.schema.json",
 "lane_concurrency_state.schema.json",
 "ARTHUR_RTK_ROUTING_PACKET.template.md",
 "LANE_CONCURRENCY_STATE.template.md"
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
arthur = next((a for a in agents if a.get("name") == "Arthur" or a.get("id") == "arthur-project-manager"), {})
if "Sonnet 4.6" not in arthur.get("llm_module", ""):
    errors.append("Arthur not set to Sonnet 4.6")
if not arthur.get("rtk_squash_required"):
    errors.append("Arthur missing RTK squash flag")
if arthur.get("max_active_lanes") != 2:
    errors.append("Arthur missing max_active_lanes=2")
if errors:
    print("ARTHUR RTK / LANE CAP VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("ARTHUR RTK / LANE CAP VALIDATION PASSED")
