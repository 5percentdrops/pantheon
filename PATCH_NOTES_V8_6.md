# V8.6 Patch Notes — Mid-pipeline QA + per-agent Dreaming

V8.5 wired every agent to a uniform `hermes_local` adapter with persistent
per-agent identity. V8.6 closes two gaps that surfaced during a multi-agent
patterns audit:

1. **Quality degrades as the pipeline lengthens.** PRD-to-SDD drift was
   being caught by Clara/Cody at PR-review time, which is too late —
   Marcus had already locked task-level TDD red tests against a flawed
   design.
2. **Skills accumulated but were never consolidated.** Each agent wrote
   skills to `~/.hermes-<slug>/skills/` post-task, but with no nightly
   review, duplicate/superseded skills piled up and `MEMORY.md` grew
   unbounded.

## What changed

### 1. Mid-pipeline QA checkpoint (Nadia after Marcus's SDD)

New stage `sdd_qa_review` inserted between `sdd_architecture` and
`tdd_block` in `Pantheon/pipelines/feature_delivery_pipeline.yaml`.

Flow:

```
... → marcus.sdd_architecture
         ↓ (emits prd_to_sdd_pipeline.schema.json)
      nadia.sdd_qa_review
         ↓ (emits sdd_qa_signoff.schema.json)
      marcus.tdd_block    ← input_contract: sdd_qa_signoff.schema.json
         ↓
      jack.implementation → clara → cody → ...
```

Hard rule: `tdd_block.input_contract = sdd_qa_signoff.schema.json`, so the
gate **cannot be bypassed** by mis-routing.

Iteration policy: Nadia may return the SDD to Marcus up to **2 times**
with cited PRD clauses. On the 3rd cycle the route escalates to Arthur,
who decides whether to scope-down the PRD or override Nadia.

New artifacts:
- `Pantheon/pipelines/feature_delivery_pipeline.yaml` — stage inserted,
  new gate `qa_sdd_signoff_required_before_tdd_block` added to `hard_gates`
- `Pantheon/routes/sdd_qa_review_routes.json` — 3 routes covering
  signoff, return, and re-entry paths
- `Pantheon/schemas/sdd_qa_signoff.schema.json` — Nadia's decision shape
  with conditional rules (approve ⇒ `blocker_count: 0`,
  escalate ⇒ `iteration: 2`)
- `scripts/validate_mid_pipeline_qa.py` — stage ordering + agent
  ownership + bypass-prevention check
- `scripts/validate.py` — wires the new validator into the chain

### 2. Nightly per-agent Dreaming (memory consolidation + skill dedup)

Every active `~/.hermes-<slug>/` now ships with a `cron/dream.cron`
entry that fires at `0 3 * * *` UTC via Hermes's per-home scheduler
(NOT system cron — no host-level coupling).

What a dream pass does:

```
pre_flight: hermes doctor (refuses to mutate a broken home)
   ↓
native_dream_if_supported: hermes dream --review-sessions 7d \
                                        --extract-patterns \
                                        --dedup-skills \
                                        --consolidate-memory \
                                        --max-tokens 8000
   ↓  (fallback when `hermes dream` subcommand not yet supported)
structural_cleanup_fallback:
   - tail-truncate MEMORY.md to 4000 lines when > 5000
   - dedup skills/*.md by sha256 (first occurrence wins)
   - write backup before any mutation
   ↓
log: $HERMES_HOME/logs/dream-YYYY-MM-DD.log
```

Invariants enforced in `Pantheon/policies/dreaming_policy.yaml`:

- **No cross-agent state read or write.** A dream pass touches one home
  only.
- **No repo write.** Only `~/.hermes-<slug>/` paths are mutable.
- **`SOUL.md`, `USER.md`, `config.yaml` are immutable** under dreaming.
- **`hermes doctor` must pass first.** A broken home is not dreamed.
- **Backup before mutation.** `.pre-dream-{utc-iso}.bak` written before
  any truncation.
- **Cooldown on failure.** A failing home is not retried for 24 h, to
  prevent broken-state amplification.
- **Owen excluded.** No model assigned, no sessions to review.

New artifacts:
- `scripts/dream_runner.sh` — per-home runner (set -euo pipefail; exits
  0/1/2/3 distinctly)
- `scripts/install_dreaming.sh` — idempotent cron installer with
  `--dry-run`, `--uninstall`, `--only`, `--hour HH`
- `Pantheon/pipelines/dreaming_pipeline.yaml` — declarative pipeline
- `Pantheon/policies/dreaming_policy.yaml` — invariants + budget +
  escalation
- `scripts/validate_dreaming.py` — verifies scripts present + executable
  + hard gates declared + installer wires it

### 3. Installer changes

`scripts/one_click_install.sh` now has 8 steps (was 7). New step 7
installs the Dreaming cron in every Hermes home that bootstrap created.

New flag: `--no-dreaming` to opt out. Implied if `--no-bootstrap` is
passed (no homes ⇒ nothing to schedule).

### 4. Manifest

```json
{
  "version": "8.6",
  "schema_version": "pantheon.v8.6",
  "prd_sdd_ticket_tdd_pipeline": {
    "nadia_sdd_review": true,
    "mid_pipeline_qa_v8_6": true
  },
  "dreaming_v8_6": {
    "enabled_by_default": true,
    "scheduler": "hermes_per_home_cron",
    "cadence": "0 3 * * * UTC",
    "excludes": ["owen"],
    "immutable_files": ["SOUL.md", "USER.md", "config.yaml"]
  }
}
```

## Bug class addressed

| Class | V8.5 behaviour | V8.6 fix |
|---|---|---|
| PRD-to-SDD drift | Caught at PR review, after TDD red tests already written against bad design | `sdd_qa_review` gates TDD on Nadia signoff; max 2 return cycles before Arthur escalation |
| Skill library duplication | Agents wrote skills freely; duplicates piled up over months | Nightly `sha256` dedup per home |
| Unbounded MEMORY.md | Heartbeats appended forever | Tail-truncate to 4000 lines when > 5000 (with backup) |
| Cross-agent state leakage risk | No formal isolation policy for memory mutations | `dreaming_policy.yaml` enforces per-home-only; SOUL/USER/config immutable |

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Nadia becomes pipeline bottleneck | 2-iteration cap + Arthur escalation; instrument iteration count in `sdd_qa_iteration_count` route field |
| `hermes dream` subcommand absent on installed version | Deterministic structural fallback (no LLM call required) |
| Dream pass corrupts an agent's memory | Backup written before every mutation; `hermes doctor` gate; `SOUL/USER/config` immutable |
| Cron timing collides on shared host | Hermes per-home scheduler serialises locally; tune via `--hour` flag if 03:00 UTC inconvenient |
| Schema bypass via mis-routed handoff | `tdd_block.input_contract = sdd_qa_signoff.schema.json` enforced; validator fails if mismatched |

## Validation

```bash
python3 scripts/validate.py        # full chain (now includes V8.6 validators)
python3 scripts/validate_mid_pipeline_qa.py
python3 scripts/validate_dreaming.py
```

End-to-end smoke: drop a PRD with a deliberate clause Marcus would miss
("must work offline for ≥ 7 days"); Marcus emits SDD; verify Nadia
returns it with `drift_findings` citing the offline clause and Marcus
re-emits.

Dreaming smoke: `bash scripts/install_dreaming.sh --dry-run` should list
32 homes (Owen excluded). Then `HERMES_HOME=~/.hermes-arthur bash
scripts/dream_runner.sh` should write a dream log.

## Rollback

Disable per-feature without reverting:

```bash
# Disable mid-pipeline QA: edit Pantheon/pipelines/feature_delivery_pipeline.yaml
# and remove the sdd_qa_review stage; revert tdd_block.input_contract.

# Disable Dreaming everywhere:
bash scripts/install_dreaming.sh --uninstall

# Re-run installer skipping V8.6 features:
bash scripts/one_click_install.sh -y --no-dreaming
```

Full revert to V8.5 is a `git revert <V8.6 commit>` away — V8.5
artifacts are untouched.
