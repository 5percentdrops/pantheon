# V8.8 Patch Notes — Escalation contracts, cross-agent learning, Maxwell override grading

V8.6 added design-time QA + per-agent dreaming. V8.7 added rubrics, fan-out,
budget watching, CMA burst spec, smoke ramp. V8.8 closes three remaining gaps
identified by the second multi-agent patterns review:

1. **Engineer→Marcus escalations were unstructured.** When Jack burned 21
   attempts and handed off, Marcus received raw conversational text. Opus
   4.7 burned input tokens parsing transcript instead of solving the
   problem.
2. **Per-agent dreams stayed per-agent.** V8.6 dreaming was deliberately
   isolated — Marcus's lessons stayed in `~/.hermes-marcus/`. Jack hit
   the same wall on the next project, burned the same DeepSeek tokens
   learning the same thing.
3. **Maxwell overrides auto-merged.** Maxwell is the most expensive agent
   in the org (Opus 4.7 Max). Silent acceptance of his fixes was the
   worst-class failure mode — no one challenged the senior.

## 1. Engineer escalation packet (rigid JSON contract)

New artifacts:

- `Pantheon/schemas/engineer_escalation_packet.schema.json` + mirror in
  `Pantheon/contracts/`
- `Pantheon/policies/escalation_packet_policy.yaml`

Required fields:

| Field | Why |
|---|---|
| `schema_version: "engineer_escalation_packet.v1"` | Marcus rejects unknown versions |
| `ticket_id` | scope identity (TKT-… pattern) |
| `agent` (enum: jack/ben/ivan/theo/leo/ellie/grant) | who escalated |
| `attempt_count` (1..21) | bounded by Jack's hard cap |
| `blocked_on` (enum: compile/runtime/test/design/dependency/ambiguous_prd) | structured failure class |
| `last_attempted_code_ref` | git SHA or path — **never inline code body** |
| `rtk_error_trace` (≤8000 chars) | RTK-compressed; raw stacks rejected |
| `tdd_red_tests[]` (minItems: 1) | no red test = no failure signal = invalid escalation |
| `marcus_handoff_format_version: "v1"` | future schema bump anchor |
| `timestamp_utc` | audit |

Conditional rules:
- `blocked_on == "dependency"` ⇒ `missing_dependencies[]` required
- `blocked_on == "ambiguous_prd"` ⇒ `self_diagnosis` required

Rejection behaviour: Marcus's runtime returns the malformed payload with
`rejected_packet_reason` populated. Engineer's attempt counter does NOT
increment on schema-rejection (the failure was the format, not the
code). After 2 schema-rejections, escalate to Arthur with rationale
`engineer cannot format escalation packet`.

Effect: handoff cost converts from `O(transcript-length)` to
`O(packet-size)`. Opus 4.7 input tokens drop accordingly.

## 2. Cross-agent dream aggregator (Winston-owned)

New artifacts:

- `scripts/dream_aggregator.py` — scrapes every
  `~/.hermes-*/logs/dream-*.log` from the last 24h and every
  `~/.hermes-*/skills/*.md` (capped 50KB/agent), extracts lessons via
  pattern regex (`bug:`, `lesson:`, `avoid …`, `always …`), dedups by
  `sha256` of normalised text, writes
  `workspace/wiki/lessons_learned.md` + `lessons_learned.index.json`.
- `scripts/install_dream_aggregator.sh` — Winston-only cron at 04:00
  UTC (1h after per-agent dreaming at 03:00, so all dreams have
  flushed).
- `Pantheon/policies/cross_agent_learning_policy.yaml`.

Read scope: every `~/.hermes-*/logs/dream-*.log` + `skills/*.md`.
Write scope: `workspace/wiki/lessons_learned.md`,
`workspace/wiki/lessons_learned.index.json`, and Winston's own home only.

Immutable across all non-Winston homes:
- `SOUL.md` / `USER.md` / `config.yaml` never read or rewritten
- No mutation of any other agent's `MEMORY.md` or `skills/*`

Dedup: `sha256(lowercase + whitespace-collapsed lesson)`. Lessons grow a
`reinforcement_field: agents` array — when multiple agents discover the
same lesson, the count rises. Lessons are **append-only** — never
deleted, auditability preserved.

Consumer hook (declarative): engineers pre-read
`workspace/wiki/lessons_learned.md` (capped at 4000 tokens of injected
context) before writing TDD red tests. Wiring of the actual injection
lives in the per-agent `seed.md` (next patch).

Smoke tested live: 32 homes scanned, **42 lessons extracted on first
run** from existing skill seeds. Aggregate written, index written, cron
installed in `~/.hermes-winston/cron/`.

## 3. Maxwell override grading (Cody re-grades against rubric)

New artifacts:

- `Pantheon/routes/maxwell_grade_routes.json` — 4 routes covering
  Maxwell→Cody, Cody pass, Cody return, Cody escalate-to-Magnus
- `Pantheon/pipelines/maxwell_override_grading_pipeline.yaml`

Flow:

```
Maxwell emits override
        ↓
Cody grades against the ticket's outcome.schema.json rubric
   (the SAME rubric Clara graded Jack's original implementation against)
        ↓
   ┌────┴────┐
   ↓         ↓
 pass     return_to_maxwell_with_notes
   ↓         ↓ (max 2 cycles)
 merge       escalate_to_magnus
             (architecture itself suspect after 2 Maxwell+Cody iterations)
```

Grader: Cody (`cody-code-escalation-reviewer`, GPT-5.5). Iteration cap:
2. Escalation: Magnus (architecture review).

Rationale: Maxwell overrides do **not** auto-merge. The merge gate is
identical whether Jack or Maxwell wrote the code — the same rubric
applies. Closes the "confident-wrong escalation" gap.

## Installer changes

- `scripts/one_click_install.sh` gains Step 7c (Winston dream aggregator
  install). Auto-runs unless `--no-dreaming` or `--no-bootstrap`.
- `scripts/validate.py` wires `validate_v8_8_patches.py`.

## Manifest

```json
{
  "version": "8.8",
  "schema_version": "pantheon.v8.8",
  "v8_8_patch": {
    "engineer_escalation_packet": {
      "schema": "Pantheon/schemas/engineer_escalation_packet.schema.json",
      "enforced_format_version": "engineer_escalation_packet.v1"
    },
    "cross_agent_learning": {
      "owner": "winston-director-knowledge-architecture",
      "cadence": "0 4 * * * UTC",
      "output": "workspace/wiki/lessons_learned.md"
    },
    "maxwell_override_grading": {
      "grader_model": "openai/gpt-5.5",
      "max_iterations": 2,
      "escalation_on_persistent_fail": "magnus-architecture-escalation"
    }
  }
}
```

## Bug class addressed

| Class | Before V8.8 | V8.8 fix |
|---|---|---|
| Unstructured escalation handoff | Marcus parsed raw transcripts; Opus tokens wasted on format inference | Rigid `engineer_escalation_packet.v1` schema; non-conforming payloads bounced; attempt counter doesn't increment on format-rejection |
| Per-agent learning siloed | Jack relearned every lesson Marcus already knew | Winston aggregates dreams across all homes; engineers pre-read `lessons_learned.md` before TDD |
| Maxwell auto-merge | Most-expensive agent's overrides skipped review | Cody re-grades against same rubric Clara used on Jack; max 2 iterations → Magnus |

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Lessons aggregate becomes noisy (false positives from regex) | `MAX_SKILL_BYTES_PER_AGENT: 50_000` cap + sha256 dedup; aggregate is markdown table, low-cost human review possible |
| Winston aggregator mutates other homes | Write scope hardcoded to `~/.hermes-winston/` + `workspace/wiki/`; validator checks policy declares non-Winston immutability |
| Maxwell-Cody loop never converges | `max_iterations: 2` hard cap + Magnus escalation |
| Engineer cannot produce packet (lacks RTK output, no red test) | Schema rejection bounces with reason; after 2 bounces escalates to Arthur |
| Aggregator runs before per-agent dreams flush | Scheduled 04:00 (1h after 03:00 dreaming); both configurable via `--hour` |

## Validation

```bash
python3 scripts/validate.py                        # full chain (17 validators)
python3 scripts/validate_v8_8_patches.py           # V8.8-only fast check
python3 scripts/dream_aggregator.py                # one-shot aggregation
bash scripts/install_dream_aggregator.sh --dry-run # preview Winston cron entry
```

Live smoke results on this host:
- Aggregator: 32 homes scanned, 42 lessons extracted, written to `workspace/wiki/lessons_learned.md`
- Winston cron: installed at `~/.hermes-winston/cron/dream_aggregator.cron`

## Rollback

Per-patch disable without revert:

```bash
# Escalation packet: edit escalation_packet_policy.yaml to mark schema optional
# Cross-agent learning: bash scripts/install_dream_aggregator.sh --uninstall
# Maxwell grading: remove route entries in maxwell_grade_routes.json (or delete the file)
```

Full V8.7 revert: `git revert <V8.8 commit>` — V8.6/V8.7 artifacts untouched.
