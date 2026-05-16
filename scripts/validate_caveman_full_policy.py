#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)

required = [
    "rules/caveman_full_agent_policy.md",
    "policies/arthur_escalation_handoff_policy.md",
    "policies/rtk_error_extract_policy.md",
    "templates/ARTHUR_SENIOR_ESCALATION_HANDOFF.template.md",
    "docs/CAVEMAN_FULL_AND_ERROR_ESCALATION.md",
]
for rel in required:
    if not (ROOT / rel).exists():
        fail(f"Missing {rel}")

policy = (ROOT / "rules/caveman_full_agent_policy.md").read_text(encoding="utf-8")
for phrase in [
    "Caveman Mode = FULL",
    "Arthur's escalation/error handoff packet",
    "CAVEMAN_MODE: EXCEPTION",
    "Caveman Lite = forbidden by default",
]:
    if phrase not in policy:
        fail(f"Caveman policy missing: {phrase}")

handoff = (ROOT / "policies/arthur_escalation_handoff_policy.md").read_text(encoding="utf-8")
for phrase in [
    "Sub-50-line failure summary",
    "Arthur → Assigned Senior Developer",
    "first 150 lines of final error",
    "last 150 lines of final error",
    "Arthur must send the available error material to the Senior Developer anyway",
]:
    if phrase not in handoff:
        fail(f"Arthur handoff policy missing: {phrase}")

rtk = (ROOT / "policies/rtk_error_extract_policy.md").read_text(encoding="utf-8")
for phrase in [
    "HEAD = first 150 lines",
    "TAIL = last 150 lines",
    "ERROR_EXTRACT_STATUS: MISSING",
    "ERROR_EXTRACT_STATUS: PARTIAL",
]:
    if phrase not in rtk:
        fail(f"RTK policy missing: {phrase}")

manifest_path = ROOT / "manifest.json"
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    caveman = manifest.get("caveman_full_policy", {})
    if caveman.get("mode") != "FULL":
        fail("manifest caveman mode must be FULL")
    if not manifest.get("arthur_escalation_handoff", {}).get("handoff_to_senior_required"):
        fail("manifest must require Arthur handoff to Senior")

print("PASS: Caveman full policy and Arthur escalation handoff validated.")
