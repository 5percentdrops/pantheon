#!/usr/bin/env python3
"""validate_v8_10_patches.py  (V8.10)

Five yellow-tier patches from the V8.9 review:

  P1. SMOKE_SCALE.md has a Phase 0 (two-agent: Arthur + Marcus).
  P2. Every pipeline YAML declares `output_budget` AND each stage with
      an agent/producer declares max_output_tokens or max_output_bytes.
  P3. Every stage with an upstream stage declares an input_contract OR
      an input_event (audit_logging emitters are runtime-event sourced,
      not schema-sourced — that's still declared, just under a
      different key).
  P4. Schema aliases `sdd.schema.json` and `test_plan.schema.json` exist
      in BOTH Pantheon/schemas/ and Pantheon/contracts/ and are pure
      $ref to the canonical schemas.
  P5. examples/weekly_market_intelligence.md exists with all 9 pipeline
      stages mentioned by name.

Exits 0 on pass, 1 on any failure.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required.", file=sys.stderr); sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
FAILS: list[str] = []

def fail(m: str): FAILS.append(m)


# --- P1: SMOKE_SCALE Phase 0 -----------------------------------------
smoke = ROOT / "SMOKE_SCALE.md"
if not smoke.exists():
    fail("SMOKE_SCALE.md missing")
else:
    text = smoke.read_text(encoding="utf-8")
    for needle in ("Phase 0: Pair (2 agents)", "Active:** Arthur + Marcus only"):
        if needle not in text:
            fail(f"SMOKE_SCALE.md missing required Phase 0 marker: {needle!r}")


# --- P2 + P3: pipeline audit -----------------------------------------
pipelines_dir = ROOT / "Pantheon" / "pipelines"
if not pipelines_dir.exists():
    fail("Pantheon/pipelines/ missing")
else:
    for yml in sorted(pipelines_dir.glob("*.yaml")):
        try:
            doc = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            fail(f"{yml.name}: YAML parse error: {e}")
            continue
        pl = doc.get("pipeline", {})

        # P2a: every pipeline declares output_budget
        if "output_budget" not in pl:
            fail(f"{yml.name}: missing pipeline.output_budget (V8.10 P2)")

        # P2b: every stage with an agent/producer declares
        #      max_output_tokens or max_output_bytes
        stages = pl.get("stages", []) or []
        for s in stages:
            stage_id = s.get("id", "<no-id>")
            if "agent" in s or "producer" in s:
                if "max_output_tokens" not in s and "max_output_bytes" not in s:
                    fail(f"{yml.name}:{stage_id} missing max_output_tokens / max_output_bytes (V8.10 P2)")

        # P3: every non-first stage with an agent declares input_contract
        #     OR input_event. (First stage may take pipeline-level input_contract.)
        for idx, s in enumerate(stages):
            if "agent" not in s and "producer" not in s:
                continue
            if idx == 0:
                # First stage: allowed to inherit from pipeline.input_contract
                if "input_contract" not in s and "input_event" not in s and "input_contract" not in pl:
                    fail(f"{yml.name}:{s.get('id')} first stage missing input_contract/input_event AND pipeline has no input_contract (V8.10 P3)")
            else:
                if "input_contract" not in s and "input_event" not in s:
                    fail(f"{yml.name}:{s.get('id')} non-first stage missing input_contract/input_event (V8.10 P3)")

        # P3b: specialist_team and fan_out pipelines must declare a
        #      pipeline-level input_contract (no stages, so no per-stage
        #      check applies).
        pattern = pl.get("pattern")
        if pattern in ("specialist_team", "fan_out") and "input_contract" not in pl:
            fail(f"{yml.name}: {pattern} pipeline missing pipeline-level input_contract (V8.10 P3)")


# --- P4: schema aliases ----------------------------------------------
for loc in ("Pantheon/schemas", "Pantheon/contracts"):
    for alias, canonical in (
        ("sdd.schema.json", "prd_to_sdd_pipeline.schema.json"),
        ("test_plan.schema.json", "task_tdd_block.schema.json"),
    ):
        p = ROOT / loc / alias
        if not p.exists():
            fail(f"{loc}/{alias} missing (V8.10 P4 alias)")
            continue
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"{loc}/{alias}: JSON parse error: {e}")
            continue
        if s.get("$ref") != canonical:
            fail(f"{loc}/{alias}: $ref must be {canonical!r}, got {s.get('$ref')!r}")


# --- P5: example doc -------------------------------------------------
example = ROOT / "examples" / "weekly_market_intelligence.md"
if not example.exists():
    fail("examples/weekly_market_intelligence.md missing (V8.10 P5)")
else:
    text = example.read_text(encoding="utf-8")
    required_stages = [
        "Context pack (Winston)",
        "PRD validation (Arthur)",
        "SDD architecture (Marcus)",
        "SDD QA review (Nadia",
        "TDD block (Marcus)",
        "Implementation (Jack",
        "Clara dual review",
        "Cody dual review",
        "Memory update (Winston)",
    ]
    for stage in required_stages:
        if stage not in text:
            fail(f"examples/weekly_market_intelligence.md missing stage marker: {stage!r}")


if FAILS:
    print("FAIL: V8.10 patches incomplete")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)

print("PASS: V8.10 yellow patches present — Phase 0 ramp, per-stage caps, bypass-proof contracts, schema aliases, example walkthrough.")
