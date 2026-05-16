# V8.9 Patch Notes — Central observability (dashboard + system outcomes + redundant work detector)

Article Step 7: *"Multi-agent systems are more complex than single agents.
More things can go wrong. Monitoring is not optional."*

V8.7 wired token-bloat alerts. V8.8 wired handoff-schema rejections.
V8.9 closes the remaining article failure modes — **quality degradation**
and **redundant work** — and rolls all four into one central surface.

## Three patches

### 1. Central metrics dashboard

- `scripts/metrics_summary.py` — pure file IO across all V8.6–V8.8 alert
  sinks (budget alerts, escalation packets, packet rejections, outcome
  grades, Maxwell override grades, dream logs, lessons learned index).
- `scripts/install_metrics_cron.sh` — Arthur-owned cron at `*/15` UTC.
- Outputs `workspace/07_Finalization/metrics_dashboard.{md,json}`.

The dashboard includes an explicit **watch list** triggered by the four
article failure modes:

| Trigger | Severity |
|---|---|
| `dream_failures_24h > 0` | 🔴 |
| `budget.crit_24h > 0` | 🔴 |
| `escalations.rejection_rate_pct > 25` | 🔴 |
| `outcomes.pass_rate_pct < 50` (with ≥4 grades) | 🟡 |
| `maxwell_overrides.escalated_to_magnus_24h > 0` | 🟡 |
| `homes_dreamed_today < total-1` (Owen excluded) | 🟡 |
| (no triggers fire) | ✅ |

Smoke run on this host: 1 watch item surfaced.

### 2. System-level Outcomes (weekly scorecard)

- `Pantheon/schemas/system_outcomes.schema.json` + `contracts/` mirror —
  org-wide rubric with 5 criteria + verdict enum
  `{healthy, watch, escalate_to_board}`.
- `scripts/system_outcomes_tracker.py` — Winston-owned cron at
  `0 6 * * 1 UTC` (Monday 06:00).
- Outputs `workspace/07_Finalization/system_outcomes_weekly.{md,json}`.

Defaults:

| Criterion | Target |
|---|---|
| Pipeline completion | ≥ 90 % |
| Avg iterations per ticket | ≤ 2.0 |
| Escalation rate | ≤ 15 % |
| CRIT budget alerts per week | 0 |
| Multi-agent reinforced lesson share | ≥ 20 % |

Verdict logic: 0 failed → healthy · 1–2 failed → watch · 3+ failed →
`escalate_to_board`. On `escalate_to_board` one line is appended to
`~/.hermes-arthur/MEMORY.md` so the human board sees it on next dispatch.

Per-ticket outcomes (V8.7) grade individual implementations.
**System outcomes (V8.9) grade the company.**

Smoke run on this host: verdict=`watch`, 1 failed criterion (insufficient
multi-agent reinforcement yet — expected, no traffic).

### 3. Redundant-work detector

Article Mistake 2: *"Multiple agents doing the same thing without realising it. Fix by making each agent's scope extremely specific."*

- `scripts/redundant_work_detector.py` — scans
  `Pantheon/paperclip/agents.json` for:
  1. Role-string near-duplicates (Jaccard ≥ 0.5)
  2. `consumes_from` / `produces_for` shared upstream **AND** downstream
  3. `seed_skill_path` duplicates (identical seeds = identical starting
     behaviour)
  4. Same model+harness pairs with overlapping role keywords (cost
     redundancy)
- Winston-owned cron at `0 5 * * 0 UTC` (Sunday 05:00).
- Outputs `workspace/07_Finalization/redundant_work_report.{md,json}`.

Advisory only — never blocks the pipeline. Findings are triage signals
for Marcus/Priya/Arthur to act on.

**First scan flagged 125 findings** on the current 33-agent roster —
not surprising for a young company. The report surfaces them
table-by-table so role descriptions can be tightened over time.

## Installer changes

- `scripts/one_click_install.sh` gains Step 7d (install observability
  crons in Arthur + Winston homes). Auto-runs unless `--no-dreaming` or
  `--no-bootstrap`.
- `scripts/validate.py` wires `validate_v8_9_patches.py` (now 18
  validators total; 17 PASS + 1 SKIP + 1 pre-existing FAIL).
- One bundled cron installer (`install_observability_crons.sh`) installs
  all three V8.9 entries; `install_metrics_cron.sh` is the single-purpose
  variant for surgical re-runs.

## Manifest

```json
{
  "version": "8.9",
  "schema_version": "pantheon.v8.9",
  "v8_9_patch": {
    "metrics_dashboard": { "cadence_minutes": 15, "owner": "arthur" },
    "system_outcomes":   { "cadence_weekly": "0 6 * * 1 UTC",
                           "verdict_enum": ["healthy","watch","escalate_to_board"],
                           "escalate_to_board_on_3plus_failed_criteria": true },
    "redundant_work_detector": { "cadence_weekly": "0 5 * * 0 UTC",
                                  "jaccard_threshold": 0.5,
                                  "advisory_only": true },
    "hard_rule": "observability NEVER calls LLM, NEVER mutates hermes homes (except Arthur MEMORY.md on escalate_to_board)"
  }
}
```

## Bug class addressed

| Article failure mode | Pre-V8.9 | V8.9 fix |
|---|---|---|
| Handoff failures | Scattered jsonl logs | Dashboard rolls them up + escalation_rate KPI in weekly outcomes |
| Redundant work | Invisible until manual review | `redundant_work_detector.py` Sun-night scan with 4 detection rules |
| Quality degradation | Per-ticket only via Clara | `system_outcomes.iteration_efficiency` tracks rolling avg across all tickets |
| Token bloat | Per-home budget alert only | Dashboard + weekly trend + CRIT count in scorecard |

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| 125-finding redundancy report demoralises | Findings are advisory; Jaccard 0.5 is conservative; tighten role descriptions over time |
| Weekly scorecard fires `escalate_to_board` on stale data | Tracker only counts events in last 7 days; healthy verdict when no traffic |
| Metrics dashboard rolls up bogus byte/4 token proxy | Documented limitation; absolute thresholds widened with 20 % headroom |
| Observability scripts mutate agent state | Hard rule in `observability_policy.yaml`; validator confirms |

## Validation

```bash
python3 scripts/validate.py                       # full chain (18 validators)
python3 scripts/validate_v8_9_patches.py          # V8.9-only fast check
python3 scripts/metrics_summary.py                # one-shot dashboard
python3 scripts/system_outcomes_tracker.py        # one-shot weekly
python3 scripts/redundant_work_detector.py        # one-shot scan
bash scripts/install_observability_crons.sh --dry-run    # preview all 3 crons
```

Live results on this host:
- Dashboard rendered to `workspace/07_Finalization/metrics_dashboard.md` (1 watch item)
- Weekly scorecard verdict: `watch` (1 failed criterion: multi-agent reinforcement)
- Redundancy report: 125 findings (advisory)
- Crons installed in `~/.hermes-arthur/cron/metrics_summary.cron` + `~/.hermes-winston/cron/{system_outcomes_weekly.cron, redundant_work_weekly.cron}`

## Rollback

```bash
bash scripts/install_observability_crons.sh --uninstall   # disable all 3
# or per-script:
bash scripts/install_metrics_cron.sh --uninstall
```

Full V8.8 revert: `git revert <V8.9 commit>` — V8.6/V8.7/V8.8 untouched.
