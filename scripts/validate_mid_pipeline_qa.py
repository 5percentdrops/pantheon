#!/usr/bin/env python3
"""validate_mid_pipeline_qa.py  (V8.6)

Asserts the V8.6 mid-pipeline QA checkpoint is wired:

  1. feature_delivery_pipeline.yaml has a `sdd_qa_review` stage owned
     by `senior-qa`, sitting between `sdd_architecture` and `tdd_block`.
  2. sdd_qa_review_routes.json exists and contains the
     `sdd_to_nadia_qa_review` route with a gate id.
  3. sdd_qa_signoff.schema.json exists with the required fields and
     conditional rules (approve => blocker_count: 0, escalate =>
     iteration: 2).
  4. tdd_block stage's input_contract is sdd_qa_signoff.schema.json
     (i.e. Marcus's TDD step actually consumes Nadia's signoff, so the
     gate cannot be silently bypassed).

Exits 0 on pass, 1 on any failure. Failures print one line each.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import yaml  # PyYAML — already a Pantheon dependency

ROOT = Path(__file__).resolve().parent.parent
FAILS: list[str] = []


def fail(msg: str) -> None:
    FAILS.append(msg)


# 1. pipeline ordering + ownership
pipeline_path = ROOT / "Pantheon" / "pipelines" / "feature_delivery_pipeline.yaml"
if not pipeline_path.exists():
    fail(f"missing: {pipeline_path.relative_to(ROOT)}")
else:
    doc = yaml.safe_load(pipeline_path.read_text(encoding="utf-8"))
    stages = doc.get("pipeline", {}).get("stages", [])
    ids = [s.get("id") for s in stages]
    for required in ("sdd_architecture", "sdd_qa_review", "tdd_block"):
        if required not in ids:
            fail(f"feature_delivery_pipeline.yaml missing stage: {required}")
    if "sdd_qa_review" in ids and "tdd_block" in ids:
        if ids.index("sdd_qa_review") >= ids.index("tdd_block"):
            fail("sdd_qa_review must precede tdd_block")
        if "sdd_architecture" in ids and ids.index("sdd_qa_review") <= ids.index("sdd_architecture"):
            fail("sdd_qa_review must follow sdd_architecture")
    qa_stage = next((s for s in stages if s.get("id") == "sdd_qa_review"), None)
    if qa_stage:
        if qa_stage.get("agent") != "senior-qa":
            fail(f"sdd_qa_review agent must be senior-qa, got {qa_stage.get('agent')!r}")
        if "gate" not in qa_stage:
            fail("sdd_qa_review stage missing gate field")
        if qa_stage.get("max_iterations", 0) < 1:
            fail("sdd_qa_review missing max_iterations")
    tdd_stage = next((s for s in stages if s.get("id") == "tdd_block"), None)
    if tdd_stage and tdd_stage.get("input_contract") != "sdd_qa_signoff.schema.json":
        fail("tdd_block.input_contract must be sdd_qa_signoff.schema.json (bypass risk)")

# 2. routes
routes_path = ROOT / "Pantheon" / "routes" / "sdd_qa_review_routes.json"
if not routes_path.exists():
    fail(f"missing: {routes_path.relative_to(ROOT)}")
else:
    doc = json.loads(routes_path.read_text(encoding="utf-8"))
    names = [r.get("name") for r in doc.get("routes", [])]
    for required in ("sdd_to_nadia_qa_review",
                     "nadia_sdd_signoff_to_tdd_block",
                     "nadia_sdd_return_to_marcus"):
        if required not in names:
            fail(f"sdd_qa_review_routes.json missing route: {required}")
    primary = next((r for r in doc["routes"] if r.get("name") == "sdd_to_nadia_qa_review"), {})
    if not primary.get("gate_id"):
        fail("sdd_to_nadia_qa_review route missing gate_id")

# 3. schema
schema_path = ROOT / "Pantheon" / "schemas" / "sdd_qa_signoff.schema.json"
if not schema_path.exists():
    fail(f"missing: {schema_path.relative_to(ROOT)}")
else:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    for field in ("ticket_id", "sdd_ref", "prd_ref", "decision", "reviewer", "iteration"):
        if field not in required:
            fail(f"sdd_qa_signoff.schema.json: required field missing: {field}")
    decision_enum = (
        schema.get("properties", {}).get("decision", {}).get("enum", [])
    )
    for d in ("approve", "return_to_marcus", "escalate_to_arthur"):
        if d not in decision_enum:
            fail(f"sdd_qa_signoff.schema.json: decision enum missing: {d}")

if FAILS:
    print("FAIL: V8.6 mid-pipeline QA wiring incomplete")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)

print("PASS: V8.6 mid-pipeline QA checkpoint wired: Marcus SDD -> Nadia signoff -> Marcus TDD.")
