# Pantheon — 3 → 33 Smoke-Scale Ramp

When you stand up Pantheon on a fresh machine, **don't fire all 33 agents on
day one**. Multi-agent failures compound silently; you want to see them at
3-agent scale, fix the wiring, then add scope.

Run the ramp in this order. Each phase has an explicit pass/fail signal —
don't move on until you see it.

---

## Phase 1: Triad (3 agents)

**Active:** Arthur + Marcus + Jack only.
**Disabled:** everyone else (Hermes per-home cron + Paperclip agent toggles).

```bash
bash scripts/one_click_install.sh -y --no-dreaming
# Then in Paperclip UI: disable all agents except arthur, marcus, jack.
```

Send the canonical smoke PRD:

> *"Build a CLI tool that counts unique words in a file."*

**Pass signal:** Arthur routes → Marcus emits SDD → Jack writes TDD red,
turns green, opens a PR. ~15 min wall time.

**Fail signals:**
- Marcus hands back to Arthur with `scope_unclear` — fix your PRD; if it
  works at this size, every later phase will scale.
- Jack hangs on test setup — fix repo template or skill seed before
  adding anyone else.
- Heartbeats drop — fix Paperclip queueing config now.

---

## Phase 2: Triad + dual review (5 agents)

**Add:** Clara + Cody.

Same PRD, plus deliberately leave one PRD clause subtle ("should also
handle BOM-prefixed UTF-8 files"). Verify Clara's first-line review
catches the gap and returns to Jack, then Cody approves on second pass.

**Pass signal:** Both reviewers fire in sequence; Jack iterates exactly
once.

**Fail signals:**
- Both reviewers approve without flagging the BOM clause → your dual
  review is performative. Tighten Clara/Cody seed prompts.
- Cody re-reviews the same thing Clara just reviewed → handoff contract
  not respected. Check `Pantheon/contracts/merge_review.schema.json`.

---

## Phase 3: + Senior QA (6 agents)

**Add:** Nadia.

This activates the V8.6 mid-pipeline QA gate. Marcus's SDD now requires
Nadia signoff before Jack touches TDD.

Send a PRD with a deliberate offline requirement that's easy to lose:

> *"Must work fully offline for ≥ 7 days; sync-on-reconnect only."*

**Pass signal:** Nadia returns Marcus's first SDD with a `drift_finding`
citing the offline clause. Marcus re-emits. Nadia approves on second
pass. Total iterations ≤ 2.

**Fail signal:** Nadia approves the first SDD even though it skipped the
offline clause → check `Pantheon/schemas/sdd_qa_signoff.schema.json` is
mounted and `must_fix_before_tdd` is required.

---

## Phase 4: + Architecture council (8 agents)

**Add:** Priya + Maxwell.

Send an architecture-dense PRD ("multi-tenant data isolation with shared
indexes"). Verify Marcus escalates to Priya for the architecture
decision, and Maxwell only activates if Cody fails ×2.

**Pass signal:** Priya's architecture note lands in
`workspace/02_SDDs/<project>_arch.md` before Marcus emits SDD.

---

## Phase 5: + Specialists on demand (15 agents)

**Add:** Safiya, Stone, Winston, Felix, Adrian, Henrik, Magnus.

Send three PRDs in parallel — one security-sensitive (auth flow), one
performance-sensitive (hot path optimization), one trading-domain (Pine
Script indicator). Verify Arthur routes by domain (not round-robin).

**Pass signal:** Auth PRD touches Safiya; perf PRD touches Stone; Pine
Script PRD goes to Felix. Winston archives all three.

---

## Phase 6: Full pantheon (33 agents, Owen excluded)

**Add:** everyone remaining.

Enable nightly Dreaming:

```bash
bash scripts/install_dreaming.sh
```

Run for one week. At end of week, inspect:

```bash
ls -la ~/.hermes-*/skills/ | wc -l                    # skill counts per home
ls ~/.hermes-*/logs/dream-*.log | head -5             # dream pass logs
cat ~/.hermes-marcus/MEMORY.md | wc -l                # memory growth
```

**Pass signal:** Skill libraries grew but no duplicates; MEMORY.md
stayed under 5000 lines per agent (Dreaming truncated as designed); no
agent in failure-cooldown state.

---

## Why not just install everything

Article-level take: multi-agent systems fail by composition, not by
individual agent. A bug that's invisible at 3-agent scale becomes a
silent quality drift at 33-agent scale. Catching it at the smallest
configuration where it can occur costs an hour; catching it after a
week of compounding bad outputs costs a re-train.

The ramp also gives you concrete numbers: time-per-PRD, token-per-PR,
escalation rates. Use those to right-size the parallel lanes and budget
caps before turning Marcus loose on fan-out.

---

## Rollback at any phase

Disable agents in Paperclip UI; the per-agent Hermes homes stay intact.
Or:

```bash
bash scripts/install_dreaming.sh --uninstall            # disable Dreaming
bash scripts/one_click_install.sh -y --no-bootstrap     # skip homes step on re-run
```

Per-agent identity (SOUL/MEMORY/USER/skills) survives reinstall.
