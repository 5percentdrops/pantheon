#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)

required = [
    "rules/arthur_head_and_hiring_policy.md",
    "docs/FULL_SOFTWARE_HOUSE_ARTHUR_HEAD.md",
    "templates/ARTHUR_HIRING_PACKET.template.md",
]
for rel in required:
    if not (ROOT / rel).exists():
        fail(f"Missing {rel}")

policy = (ROOT / "rules/arthur_head_and_hiring_policy.md").read_text(encoding="utf-8")
for phrase in [
    "Arthur = Project Manager / Head",
    "Arthur is the only role allowed to hire",
    "Arthur must not quietly expand the team",
    "No hidden hires",
]:
    if phrase not in policy:
        fail(f"Arthur head policy missing: {phrase}")

manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
head = manifest.get("arthur_head", {})
if head.get("title") != "Project Manager / Head":
    fail("Arthur title must be Project Manager / Head")
if head.get("paperclip_ceo_role_renamed_to") != "Arthur":
    fail("Paperclip CEO role must be renamed to Arthur")
if not head.get("hiring_authority", {}).get("requires_hiring_packet"):
    fail("Arthur hiring must require hiring packet")

routes = json.loads((ROOT / "routes/v7_routing_matrix.json").read_text(encoding="utf-8"))
arthur = routes.get("arthur_head", {})
if not arthur.get("can_activate_specialists"):
    fail("Arthur specialist activation authority missing")
if not arthur.get("requires_hiring_packet"):
    fail("Arthur hiring packet requirement missing")

print("PASS: Full Software House Arthur head and hiring authority validated.")
