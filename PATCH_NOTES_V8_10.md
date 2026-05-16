# V8.10 Patch Notes — Yellow-tier hardening: Phase 0, per-stage caps, bypass-proof contracts, schema aliases, example walkthrough

V8.9 review surfaced five yellow-priority gaps from the article framework.
V8.10 closes all five. No new agents, no new runtime — pure tightening of
the existing pipeline + contract surface.

## What changed

### 1. SMOKE_SCALE Phase 0 — 2-agent pilot

Article Step 6 explicitly recommends *"Start with TWO agents working
together on a simple pipeline task."* Pantheon V8.7's smoke ramp started
at 3 agents (Arthur + Marcus + Jack), which already includes engineer
risk.

V8.10 inserts **Phase 0** at the top of `SMOKE_SCALE.md`:

- Active: Arthur + Marcus only (Jack disabled)
- Trivial PRD: `function add(a, b) -> int`
- Pass signal: Arthur → Marcus SDD → Nadia signoff → Arthur archive
  in < 5 min
- Verifies the handoff contract surface (`prd.schema.json` →
  `paperclip_issue.schema.json` → `prd_to_sdd_pipeline.schema.json`)
  before any engineer-side complexity

Phase 0 must pass cleanly **twice with different toy PRDs** before
moving to Phase 1's triad.

### 2. Per-stage `max_output_tokens` enforced across every pipeline

Article Mistake 5 (token bloat): *"Agents generating unnecessarily
verbose output that eats token limits. Fix by adding constraints on
output length."*

Pre-V8.10 we had per-agent daily caps (`budget_policy.yaml`) but no
per-output length enforcement at the pipeline level. V8.10 adds an
`output_budget` block to every pipeline AND a `max_output_tokens` (or
`max_output_bytes` for emitter pipelines) to every stage that owns an
agent or producer.

Caps chosen to bound the legitimate stage class:

| Stage class | Default cap | Reason |
|---|---|---|
| Context pack / memory update (Winston Haiku) | 2 000–4 000 | Compact summaries |
| PRD / paperclip_issue / governance (Arthur GPT-5 mini) | 2 000 | Routing artifacts are short |
| SDD architecture (Marcus Opus 4.7) | 12 000 | Design docs can be long, capped to prevent essay drift |
| TDD block (Marcus) | 6 000 | Test plans are structured lists |
| Implementation (Jack DeepSeek) | 16 000 | Largest legitimate stage |
| Dual review (Clara/Cody) | 4 000 | Reviews cite, not narrate |
| Nadia QA signoff | 4 000 | Decision + drift findings |
| Maxwell override | 16 000 | Most expensive lane; explicit cap critical |
| Specialist team (architecture council) | 6 000 per specialist | Bounded contributions |
| Red-team fan-out | 6 000 per fan-out | Bounded reviews |
| Audit emitters (heartbeat/transcript/budget) | 4 KB / 32 KB / 1 KB | Structural byte cap, not tokens |
| Observability | 1 MB total bytes (pure file IO) | No LLM tokens; cap protects file growth |
| Dreaming | 8 000 | Matches native `hermes dream --max-tokens` arg |

`hard_gates` for each pipeline now include
`per_stage_max_output_tokens_enforced` (or `per_producer_max_output_bytes_enforced`
for emitters).

### 3. Bypass-proof `input_contract` on every stage

V8.6 made the SDD→TDD handoff bypass-proof by setting
`tdd_block.input_contract = sdd_qa_signoff.schema.json`. V8.10 extends
the same invariant to every stage in every pipeline:

- Every non-first stage declares `input_contract` (the schema it
  consumes) OR `input_event` (for emitter pipelines whose inputs are
  runtime events, not schemas).
- First stages may inherit from a pipeline-level `input_contract`
  (added on `architecture_council_pipeline.yaml` and
  `red_team_fanout_pipeline.yaml`).
- Audit emitter stages (`emit_heartbeat`, `emit_transcript`,
  `emit_budget_event`) declare `input_event` so the runtime source is
  explicit even though there's no upstream schema.

Effect: Marcus's runtime cannot accept an outcome_grade in place of a
TDD block; Cody's review cannot accept an SDD in place of an
implementation_report; etc. Wrong-handoff routing fails fast at schema
validation rather than wasting Opus tokens parsing the wrong shape.

Pipelines audited (9): feature_delivery, ci_triage,
architecture_council, red_team_fanout, maxwell_override_grading,
model_route_override, audit_logging, memory_hygiene, dreaming,
observability.

### 4. Schema name aliases (`sdd.schema.json` + `test_plan.schema.json`)

The V8.8 audit noted that summary docs reference `sdd.schema.json` and
`test_plan.schema.json` — names that match the article's mental model —
but Pantheon stores them as `prd_to_sdd_pipeline.schema.json` and
`task_tdd_block.schema.json`. New users (and grep) lose.

V8.10 ships pure `$ref` alias files in BOTH
`Pantheon/schemas/` and `Pantheon/contracts/`:

```json
{ "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "sdd.schema.json",
  "$ref": "prd_to_sdd_pipeline.schema.json" }
```

No duplication — only one canonical shape. The aliases resolve via
JSON Schema `$ref` rules. Tooling that doesn't follow `$ref` still
finds the file (it's not a redirect; it's a real file with a
descriptive title). The validator confirms `$ref` exactly equals the
canonical name.

### 5. Example walkthrough — `examples/weekly_market_intelligence.md`

The article's most concrete example was a "Weekly Market Intelligence
Report" produced by 6 collaborating agents. V8.10 ships an analogous
walkthrough mapped onto Pantheon's 33-agent org:

- Full pipeline trace stage-by-stage (Context pack → PRD validation →
  SDD → SDD QA → TDD → implementation → dual review → memory update)
- Projected token/wall-time per stage, derived from V8.10 `max_output_tokens` caps + nominal model latencies
- Sequential vs V8.7 fan-out projections (~22 min vs ~14 min wall time)
- Sample dashboard view at Monday 08:00 UTC
- Explicit disclaimer: numbers are projections from caps, not
  measurements. Replace with live data from
  `workspace/07_Finalization/metrics_dashboard.json` after first real run.

## Bug class addressed

| Class | Before V8.10 | V8.10 fix |
|---|---|---|
| Day-1 onboarding fires too many agents | Smoke ramp started at 3 agents | Phase 0 = 2 agents (Arthur + Marcus) verifies handoff before engineer risk |
| Unbounded output per stage | Per-day caps only | `max_output_tokens` (or `_bytes`) on every stage; `output_budget` per pipeline |
| Mis-routed handoffs absorb tokens | Some stages had no `input_contract` | Every non-first stage now declares `input_contract` or `input_event`; specialist/fan-out pipelines declare pipeline-level `input_contract` |
| Schema mental-model mismatch | Doc references `sdd.schema.json` but file was `prd_to_sdd_pipeline.schema.json` | `$ref` aliases shipped in both `schemas/` and `contracts/` |
| No concrete example | SMOKE_SCALE described phases abstractly | `examples/weekly_market_intelligence.md` with stage-by-stage projections |

## Validation

```bash
python3 scripts/validate.py                       # full chain (19 validators)
python3 scripts/validate_v8_10_patches.py         # V8.10-only fast check
```

Live result on this host: V8.10 validator PASS. Full chain: 18 PASS + 1
SKIP (`pantheon/` post-converter) + 1 pre-existing FAIL
(`validate_v7_pipeline.py` workspace folders; installer creates at
runtime — unrelated).

## Manifest

```json
{
  "version": "8.10",
  "schema_version": "pantheon.v8.10",
  "v8_10_patch": {
    "smoke_phase_0_pair":            { "agents": ["arthur","marcus"] },
    "per_stage_output_caps":         { "invariant": "every stage declares max_output_tokens or max_output_bytes" },
    "bypass_proof_input_contracts":  { "pipelines_audited": 9 },
    "schema_aliases":                { "sdd.schema.json": "->prd_to_sdd_pipeline.schema.json", "test_plan.schema.json": "->task_tdd_block.schema.json" },
    "example_walkthrough":           "examples/weekly_market_intelligence.md"
  }
}
```

## Rollback

V8.10 is non-runtime hardening — only YAML/JSON/MD changes. To soften
any single rule:

- Remove the `output_budget` block from a specific pipeline to lift the
  cap on that pipeline.
- Remove `max_output_tokens` from a specific stage to lift the cap on
  that stage.
- Remove a stage's `input_contract` to revert to pre-V8.10 bypass-
  permissive behavior (NOT recommended — breaks the V8.6 SDD→TDD
  invariant if you remove the wrong one).
- Delete the alias files in `Pantheon/{schemas,contracts}/{sdd,test_plan}.schema.json`
  to revert to canonical-name-only.

Full V8.9 revert: `git revert <V8.10 commit>` — V8.6–V8.9 untouched.
