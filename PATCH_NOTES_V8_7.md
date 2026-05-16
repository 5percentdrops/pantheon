# V8.7 Patch Notes — Rubric grading, fan-out, budget watching, CMA burst, smoke ramp

V8.6 added the design-time QA gate (Nadia after Marcus's SDD) and per-agent
nightly Dreaming. V8.7 ships the remaining patches from the multi-agent
patterns audit:

1. **Outcome rubric** — Clara grades implementations against machine-checkable
   criteria; auto-iterates with Jack up to N times before passing to Cody.
2. **Fan-out engineer pool** — Marcus's no-dependency tickets can dispatch
   across 4 parallel engineers instead of serialising on Jack.
3. **Per-host budget watcher** — Arthur owns budget oversight; emits WARN at
   80%, CRIT at 95%, writes to Arthur's MEMORY.md.
4. **Claude Managed Agents burst lane** — declarative spec + adapter stub
   for Marcus to fan out ≥5 Opus heads in parallel when an SDD has >8
   subsystems. Spec-only today; auto-falls-back to serial decomposition
   until the Anthropic CMA endpoint is wired.
5. **SMOKE_SCALE.md** — 6-phase 3→33 agent ramp doc so you don't fire all
   33 on day one and try to diagnose composition failures.

## 1. Outcome rubric

New artifacts:

- `Pantheon/schemas/outcome.schema.json` — per-ticket rubric attached by
  Marcus. Required fields: `ticket_id`, `must_have`, `rubric_score_min`
  (default 0.85), `grader` (Clara only), `max_iterations` (1..5).
  Optional: `must_not`, `scope_paths`, `iterate_on_fail`,
  `escalation_on_persistent_fail` (default Cody).
- `Pantheon/schemas/outcome_grade.schema.json` — Clara's emitted grade.
  Required: `score`, `per_criterion[]` (with concrete evidence), `decision`
  (`pass_to_cody` | `return_to_jack` | `escalate`). Conditional rules
  enforce that `pass_to_cody` requires `score ≥ 0.85` and
  `return_to_jack` requires both `per_criterion` and `return_notes`.
- `Pantheon/policies/outcome_grading_policy.yaml` — `rubric_required:
  true` per ticket; hard rules forbid the implementer from grading their
  own implementation; cost attribution per ticket.

Effect: Clara's review surface shifts from "looks fine to me" to
machine-graded criteria with cited evidence. Jack iterates against the
rubric before Cody ever sees the PR.

## 2. Fan-out engineer pool

New: `Pantheon/policies/parallel_dispatch_policy.yaml`.

Pool (7 engineers, DeepSeek V4 Pro under Hermes): Jack, Ben, Ivan, Theo,
Leo, Ellie, Grant.

Dispatch rules:

- Only dispatch tickets where `dependency_graph.depends_on == []`.
- Serial fallback on shared-file lock contention (detected via git
  index).
- Each parallel lane gets its own outcome rubric instance.
- Clara grades all lanes; aggregate roll-up to one PR.
- Per-lane token cap = per-ticket cap (parallel doesn't inflate budget).

Arthur's standing "≤2 active engineering lanes" rule relaxes to ≤4 only
when fan-out is active. **Disabled by default** — opt in per project
after Phase 5 of the smoke ramp.

## 3. Per-host budget watcher

New artifacts:

- `scripts/budget_watcher.py` — sums today's session bytes per home,
  divides by 4 (token proxy), compares to per-agent cap from
  `Pantheon/company/budget_policy.yaml`, emits alerts.
- `scripts/install_budget_watcher.sh` — installs an Arthur-only cron
  entry at `~/.hermes-arthur/cron/budget_watcher.cron`, runs every
  30 min (configurable 1..60). `--dry-run`, `--uninstall`,
  `--interval N`.

Alert sinks:

1. `workspace/07_Finalization/budget_alerts.jsonl` (append-only,
   structured).
2. `~/.hermes-arthur/MEMORY.md` on CRIT — Arthur reads this on next
   dispatch.
3. stderr fallback.

Thresholds: WARN ≥ 80%, CRIT ≥ 95%. Watcher never spends tokens, never
calls an LLM, pure file IO. Smoke-tested today: scanned 32 homes, 0
alerts (expected — no agent traffic yet).

## 4. Claude Managed Agents burst lane (spec)

`Pantheon/harnesses/claude_managed_burst.yaml` — declarative contract
for Marcus's runtime. Trigger: SDD with `subsystem_count > 8`. Children:
≤5 parallel Opus 4.7 instances each capped at 60k tokens. Merge: Marcus
synthesizes back into the standard `prd_to_sdd_pipeline.schema.json` so
downstream agents see no difference between serial and bursted SDDs.

`scripts/claude_managed_burst_adapter.py` is a stub that returns
`burst_unavailable` + `fallback: marcus_sequential_decomposition` today.
The interface is fixed; replace the function body once the Anthropic CMA
endpoint URL is stable and `ANTHROPIC_API_KEY` is provisioned.

Guardrails baked in:

- CMA children cannot write to `~/.hermes-marcus/` directly.
- CMA children cannot invoke other Pantheon agents.
- Burst disabled when `budget_watcher` reports CRIT.
- Max 1 active burst per host.
- Hermes remains the identity layer; CMA is borrowed parallel infra only.

## 5. SMOKE_SCALE.md

Six-phase ramp from 3 agents (Arthur + Marcus + Jack) to all 33. Each
phase has a deliberate failure mode to verify (BOM-prefixed UTF-8,
offline-7d requirement, multi-tenant data isolation, etc.) so you don't
discover composition bugs at week-3 scale.

## Installer changes

- `scripts/one_click_install.sh` gains Step 7b (budget watcher install).
  Auto-runs unless `--no-dreaming` (which also gates the budget watcher,
  since both rely on per-home cron) or `--no-bootstrap`.
- `scripts/validate.py` wires `validate_v8_7_patches.py`.

## Manifest

```json
{
  "version": "8.7",
  "schema_version": "pantheon.v8.7",
  "v8_7_patch": {
    "outcome_rubric": { ... },
    "parallel_dispatch": { "enabled_by_default": false, "engineers_pool_size": 7, "max_parallel_lanes": 4 },
    "budget_watcher": { "cadence_minutes": 30, "warn_threshold_pct": 80, "crit_threshold_pct": 95 },
    "claude_managed_burst": { "status": "spec_only_pending_anthropic_cma_endpoint" },
    "smoke_ramp_doc": "SMOKE_SCALE.md"
  }
}
```

## Bug class addressed

| Class | Before V8.7 | V8.7 fix |
|---|---|---|
| Review = opinion | Clara/Cody approve on judgment | Rubric with cited evidence per criterion |
| Idle parallelism | Jack serialised independent tickets | 4-way fan-out across DeepSeek engineer pool |
| Budget blind spot | Per-agent caps existed but no live monitor | 30-min watcher + WARN/CRIT thresholds to Arthur |
| No burst capacity | Marcus serial-decomposes 20-subsystem SDDs | CMA burst spec + adapter stub + auto-fallback |
| Day-1 33-agent firehose | New users hit composition bugs at full scale | Phased 3→33 smoke ramp with deliberate failure modes |

## Validation

```bash
python3 scripts/validate.py                  # full chain (now 16 validators)
python3 scripts/validate_v8_7_patches.py     # V8.7-only fast check
python3 scripts/budget_watcher.py            # one-shot run, prints alert count
echo '{"subsystems":["a","b"]}' | python3 scripts/claude_managed_burst_adapter.py
```

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Rubric scoring becomes Clara's judgment dressed up as score | `per_criterion[].evidence` must cite file:line or commit SHA; vague returns fail schema |
| Fan-out causes file-lock contention | Serial fallback on git-index contention; engineers_pool limited to backend lane |
| Budget watcher misses tokens (byte proxy ≠ exact tokens) | Documented limitation; WARN at 80% gives 20% headroom for proxy error |
| CMA burst is invoked before stub is replaced | Stub returns `burst_unavailable` + structured fallback; Marcus runtime falls back cleanly |
| Smoke ramp ignored | Documented as recommended, not enforced — users can still install all 33 directly; ramp is for diagnosing failures |

## Rollback

Per-patch disable without revert:

```bash
# Outcome rubric: edit outcome_grading_policy.yaml -> rubric_required: false
# Fan-out: edit parallel_dispatch_policy.yaml -> enabled_by_default: false (already default)
# Budget watcher: bash scripts/install_budget_watcher.sh --uninstall
# CMA burst: already inert (stub returns unavailable)
# Smoke ramp: documentation; nothing to disable
```

Full V8.6 revert: `git revert <V8.7 commit>` — V8.6 artifacts untouched.
