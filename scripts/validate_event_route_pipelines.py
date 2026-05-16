#!/usr/bin/env python3
"""
Assert every value in routes.event_routes resolves to a pipeline file whose
declared `id:` field matches.

V8.1 had this check; V8.2 dropped it; V8.2 also added two event_route entries
(model_route_override_v8_2, audit_logging_v8_2) whose pipelines did not exist.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SH = ROOT / "Pantheon"

routes = json.loads((SH / "routes" / "paperclip_control_plane_routes.json").read_text(encoding="utf-8"))
event_routes = routes.get("event_routes", {})

# Collect actual pipeline ids
pipeline_ids = {}
for pf in (SH / "pipelines").glob("*.yaml"):
    txt = pf.read_text(encoding="utf-8")
    m = re.search(r"^\s*id:\s*(\S+)", txt, flags=re.M)
    if m:
        pipeline_ids[m.group(1)] = str(pf.relative_to(ROOT))

missing = []
for event, pid in event_routes.items():
    if pid not in pipeline_ids:
        missing.append((event, pid))

if missing:
    print(f"FAIL: {len(missing)} event_route(s) reference pipeline ids with no matching pipeline file:")
    for event, pid in missing:
        print(f"  {event!r} -> {pid!r}")
    print(f"\nKnown pipeline ids: {list(pipeline_ids.keys())}")
    sys.exit(1)

print(f"PASS: all {len(event_routes)} event_routes resolve to existing pipeline files.")
