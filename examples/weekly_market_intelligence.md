# Worked Example: Weekly Market Intelligence Report

A concrete end-to-end walkthrough so you can see what "Pantheon ships a PR" actually looks like. Mirrors the article's "Weekly Market Intelligence Report" use case, run through Pantheon's 33-agent org.

> **Scope of this doc:** illustrative, not a benchmark.
> The token/time numbers below are *projected from the V8.10 `output_budget` caps and per-agent model assignments*, not measured. Treat them as upper bounds for capacity planning. Replace with live numbers from `workspace/07_Finalization/metrics_dashboard.md` after your first real run.

---

## The PRD

```text
PROJECT: weekly-market-intel
TYPE:    research_pipeline
GOAL:    Produce a Monday-morning briefing covering 5 named competitors.
         Must include: pricing change since last Monday, new product launches,
         funding rounds, hiring signals on LinkedIn, social sentiment (X).
         Output: one Markdown file with executive summary + competitor sections.
         SLA:     report lands in workspace/06_Project_Repos/weekly_intel/ by 08:00 UTC every Mon.
COMPETITORS: A, B, C, D, E
```

Submit via Paperclip UI → Arthur. No human touch from this point until merge gate.

---

## Pipeline trace

### Stage 1 — Context pack (Winston)

| Field | Value |
|---|---|
| Agent | `winston-director-knowledge-architecture` |
| Model | Claude 3.5 Haiku |
| Cap (V8.10) | 4000 output tokens |
| Reads | `PROJECT.yaml`, `workspace/wiki/lessons_learned.md` (V8.8 cross-agent), prior weekly intel runs |
| Emits | `context_pack.schema.json` instance |
| Projected wall time | 45 s |

Winston flags 3 lessons from prior runs (e.g. *"Competitor C's status page returns 503 every Sun → use cached snapshot before 23:00 Sun UTC"*).

### Stage 2 — PRD validation (Arthur)

| Field | Value |
|---|---|
| Agent | `arthur-project-manager` |
| Model | GPT-5 mini |
| Cap | 2000 |
| Emits | `paperclip_issue.schema.json` with 5 competitor sub-issues |
| Projected wall time | 20 s |

### Stage 3 — SDD architecture (Marcus)

| Field | Value |
|---|---|
| Agent | `marcus-senior-backend-developer` |
| Model | Opus 4.7 |
| Cap | 12 000 |
| Emits | `prd_to_sdd_pipeline.schema.json` — describes the 5 fetcher modules + the synthesis module |
| Projected wall time | 2 min |

### Stage 4 — SDD QA review (Nadia, V8.6)

| Field | Value |
|---|---|
| Agent | `senior-qa` (Nadia) |
| Model | Opus 4.7 XHigh |
| Cap | 4000 |
| Decides | `approve` / `return_to_marcus` / `escalate_to_arthur` |
| Projected iterations | 1 (clean PRD) or 2 (Nadia returns once for the cached-snapshot lesson) |
| Projected wall time | 90 s (iter 1) or 4 min (iter 2) |

If Nadia returns, Marcus re-emits incorporating the missed clause. Iteration count appears in the dashboard.

### Stage 5 — TDD block (Marcus)

| Field | Value |
|---|---|
| Agent | `marcus-senior-backend-developer` |
| Cap | 6000 |
| Emits | `task_tdd_block.schema.json` with red tests for each fetcher + synthesis |
| Projected wall time | 90 s |

### Stage 6 — Implementation (Jack OR fan-out pool)

**Sequential (default):**
- Agent `jack-backend-developer` (DeepSeek V4 Pro)
- Cap 16 000 (largest legitimate stage per V8.10)
- Five fetchers + synthesis written serially: ~12 min

**Fan-out (V8.7, opt-in):**
- 4 lanes from `engineers_pool` (Jack, Ben, Ivan, Theo)
- Each writes one independent fetcher in parallel
- Lane 5 (Leo) writes the synthesis after lanes 1–4 settle
- Total wall time: ~5 min

Outcome rubric (V8.7) gates each: must pass red tests, must respect `scope_paths` (each lane confined to its fetcher's folder).

### Stage 7 — Clara dual review (Opus 4.7)

| Cap | 4000 |
| Grades against `outcome.schema.json` per ticket |
| Returns to Jack if `score < 0.85` (V8.7) |
| Projected pass rate (first try, clean Phase-2-equivalent ramp) | 70 % |

### Stage 8 — Cody dual review (GPT-5.5 Codex)

| Cap | 4000 |
| Re-grades on same rubric |
| Failure escalates to Maxwell after Cody fails ×2 |

### Stage 9 — Memory update (Winston)

| Cap | 2000 |
| Emits | `memory_update.schema.json` — new lessons added to per-home stores |
| At 03:00 UTC: per-agent Dreaming consolidates (V8.6) |
| At 04:00 UTC: Winston aggregates cross-agent (V8.8) |

---

## Projected aggregate

| Metric | Sequential | Fan-out (V8.7) |
|---|---|---|
| Wall time, happy path | ~22 min | ~14 min |
| Wall time, with one Nadia return + one Clara return | ~35 min | ~22 min |
| Total output tokens (pipeline_total_max_tokens cap = 60 000) | ~45 000 | ~50 000 |
| Token cost (mixed Opus + GPT-5 mini + DeepSeek + Haiku, mid-2026 rates) | ~$0.80 – $2.00 | ~$1.00 – $2.50 |

V8.7 budget watcher fires WARN at 80 % of Arthur's daily cap regardless of the per-run cost.

---

## What you'd actually see

Monday 08:00 UTC, the dashboard says:

```
workspace/07_Finalization/metrics_dashboard.md

🚨 Watch list (last 24h):
  ✅ no monitored failure modes triggered in last 24h

📊 Headline numbers:
  Homes dreamed today:  32/32
  Sessions tokens today (byte/4 proxy):  48 712
  Lessons learned (cumulative):           67
  Lessons reinforced across ≥2 agents:    14

📐 Outcome rubric grading (24h):
  Graded:     6
  Passed:     5
  Returned:   1
  Pass rate:  83.3%
```

And in `workspace/06_Project_Repos/weekly_intel/2026-05-18.md`:

```markdown
# Weekly Market Intelligence — 2026-05-18

## Executive summary
Competitor C raised $40M Series B on Wed; pricing unchanged.
Competitor A dropped enterprise tier 18%, kept free tier identical.
Competitor B shipped collaboration feature; sentiment on X mixed (62/38 +/-).
…
```

---

## When this example does NOT apply

- You haven't completed `SMOKE_SCALE.md` Phase 0 + Phase 1 yet — don't try this until Arthur + Marcus + Jack handoffs are clean.
- You haven't provisioned API keys via `setup_api_keys.sh` — fetchers will fail silently if no `ANTHROPIC_API_KEY` / `OPENROUTER_API_KEY`.
- You haven't enabled fan-out per project (V8.7 opt-in) — the parallel numbers above assume `parallel_dispatch_policy.yaml.enabled_by_default: true` for this project's lane.

---

## Replace these numbers

The token/time figures above are projected from V8.10 caps + nominal model latencies. After your first real run, copy the actual values from `workspace/07_Finalization/metrics_dashboard.json` into this doc so future planning uses empirical data.
