# Hermes Skill Library — How the Learning Loop Works

Every reasoning agent in the house runs on Hermes. Hermes maintains `skills_library` — a Supabase table where agents log reusable patterns, runbooks, failure modes, and recipes. This is what makes the house compound across builds instead of starting from scratch every time.

---

## What Lives in the Skill Library

Five categories, tagged per entry:

| Category | Example |
|---|---|
| `pattern` | "Fair Value Gap detection — 3-bar imbalance logic in Pine v5" |
| `runbook` | "AWS eu-west-1 deploy for sub-1ms latency trading infra" |
| `failure-mode` | "Pine `request.security()` with default lookahead causes repainting" |
| `recipe` | "Karpathy autoresearch loop for ICT SL optimisation — params + convergence rule" |
| `experiment` | "Session sweep + FVG on BTC 15m — 2024 walk-forward results" |

Each entry carries:

- `agent_id` — who logged it
- `domain` — backend / frontend / pinescript / devops / data / backtest / etc.
- `title`
- `description` — one-liner
- `when_to_use` — situations where this applies
- `content` — full markdown body with code refs
- `code_refs` — pointers to canonical implementations in the repo
- `tags` — searchable
- `success_count` / `failure_count` — updated as the pattern gets reused

---

## Who Writes Skills

Every Hermes agent writes to `skills_library` at specific moments:

### Senior Advisors (Opus 4.7)

After each build, log:

- Plans that worked cleanly → promote to `pattern`
- Recurring failures caught in review → log as `failure-mode`
- Novel architectural decisions that should be reusable → `pattern`
- Cross-desk coordination moves that succeeded → `recipe`

### Executors (Opus 4.6 / Sonnet / Kimi / Haiku)

While working, log:

- Library quirks and workarounds → `failure-mode`
- Reusable code blocks they produced → `pattern` with `code_refs`
- Tricky debugging sessions once resolved → `failure-mode`

### Project Manager

After each build closes, write the post-mortem as a structured `experiment`-type entry:

- Build ID + summary
- What the PRD asked for vs what shipped
- What went smoothly
- What caused rework
- Reusable patterns discovered
- Failure modes hit

---

## How Skills Get Used

### At plan-writing time

Senior Advisor starts writing a plan. Before composing from scratch, Hermes queries `skills_library` by domain + tags:

```sql
select * from skills_library
where domain = 'pinescript'
  and (tags && array['fvg', 'session-sweep', 'ict'])
  and category in ('pattern', 'recipe')
order by success_count desc, updated_at desc
limit 10;
```

Returned skills get pulled into the Senior's context. The plan then references them:

> Entry logic follows the FVG detector pattern from skill `fvg-3bar-pine-v5` (skill_id: abc123). Session filter uses `ict-london-ny-sessions` pattern.

Instead of rewriting an FVG detector, the plan composes from existing parts.

### At execution time

Executor reads the plan. Sees the skill references. Pulls the skill content + code refs. Reuses the canonical implementation rather than reimplementing.

### At review time

Senior Advisor reviews the PR. Checks: did the Executor use the referenced skills correctly? Did the Executor introduce a new pattern worth logging?

---

## The Compounding Curve

```
  Build 1
    patterns logged: 20       total: 20
    reuse rate: 0%            plan-writing time: baseline
    
  Build 2
    reused: 12   new: 18      total: 38
    reuse rate: 40%           plan-writing time: -20%
    
  Build 3
    reused: 28   new: 15      total: 53
    reuse rate: 65%           plan-writing time: -35%
    
  Build 5
    reused: 64   new: 11      total: ~110
    reuse rate: 85%           plan-writing time: -55%
    
  Build 10
    reused: 140  new: 8       total: ~220
    reuse rate: 94%           plan-writing time: -70%
```

By build 10, planning is mostly composition. The Senior PineScript Dev isn't designing FVG detectors — it's instantiating the canonical one. The Senior DevOps isn't writing AWS setups — it's parameterising a proven template. Execution speed and reliability both climb with the curve.

---

## Skill Hygiene

The library compounds value, but stale skills rot. Senior Advisors are responsible for hygiene:

### After every use, mark outcome

```
skill pulled → used successfully → success_count += 1
skill pulled → didn't apply / caused issue → failure_count += 1 + note
```

### Deprecate when pattern becomes wrong

If a pattern stops working (library upgrade, platform change, new best practice), the Senior Advisor:

1. Updates the skill entry: `status = 'deprecated'`, notes the reason
2. Adds a replacement pointer if applicable: `superseded_by = new_skill_id`
3. Flags the deprecation in the next PM post-mortem

### Quarterly review (PM-owned)

Every 3 months, PM runs a skills review:

- Highest `success_count` skills: promote to canonical status (first result in searches)
- Highest `failure_count` skills: investigate why, deprecate or rewrite
- Unused skills (>90 days no reuse): archive
- Missing skills (patterns that keep getting reimplemented): flag for explicit logging next time

---

## What This Looks Like in Practice

**Example: building a new ICT strategy after the house has run 5 builds**

1. You send PRD: "Build ICT session sweep + OB confluence strategy on ETH 5m"

2. PM routes to Senior PineScript Dev + Senior Backtester

3. Senior PineScript Dev queries `skills_library` by domain='pinescript', tags includes 'ict':

   - Returns: `ict-session-sweep-detector` (v2, used 4 times, 4 success / 0 fail)
   - Returns: `order-block-identification` (v3, used 6 times, 5 success / 1 fail — documented failure case)
   - Returns: `structural-sl-placement-fvg-ob` (v1, used 2 times, 2 success / 0 fail)

4. Plan composes from these skills + adds the new combination logic (confluence scoring). Much faster than writing from scratch.

5. PineScript Developer implements. Most of the code is imports + wiring. Net-new code is the confluence scoring module.

6. Senior Backtester queries `skills_library` for 'karpathy-autoresearch' recipes:

   - Returns: `karpathy-autoresearch-ict-params` (used 3 times, convergence criteria refined build 3, now optimal)

7. Runs the experiment with known-good recipe. Produces GREEN/YELLOW/RED quickly.

8. Build closes. Two new skills logged:

   - `confluence-scoring-module` — the net-new code block, reusable for future multi-indicator strategies
   - `eth-5m-session-edge-cases` — failure-mode doc for timezone drift specific to ETH on 5m

**Build 6 cost: ~40% of what build 1 cost, for a strategy that's more complex.**

That's the compounding.

---

## Why This Beats Stateless Agents

Most multi-agent systems treat each run as fresh. Every prompt starts the model from scratch. Every build reinvents what the last build figured out.

Hermes + `skills_library` turns the house into a cumulative system. The PM's post-mortem discipline is the engine. Every build adds to the corpus. Every plan reads the corpus before writing. The 10th build stands on the shoulders of the 9 before it.

This is the whole reason the house runs on Hermes instead of plain API calls. **Hermes remembers. Plain API calls don't.**
