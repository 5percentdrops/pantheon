# Kickstart — How to Feed Work Into Software House

The Software House is a service. Drop in specs, get working code out. This doc shows exactly what "drop in specs" means and what to expect back.

---

## What You Provide

Three artefacts per build:

1. **`PRD.md`** — Product Requirements Document. What you're building, for whom, acceptance criteria, scope.
2. **`SDD.md`** — Software Design Document. Architecture, tech stack, data model, APIs, integrations, performance targets.
3. **`/jsx/`** — Your front-end draft. JSX files iterated in ChatGPT / Claude / wherever you draft design. Can be rough — the Senior Frontend Developer tightens them into production components.

Put these in `~/[house-slug]/builds/[build-slug]/`.

Optionally, you can pre-write tickets yourself in `~/[house-slug]/builds/[build-slug]/tickets/`. The PM will accept them instead of generating its own.

---

## The Handoff Message

Open Paperclip. Message the Project Manager:

```
New build.

Path: ~/[house-slug]/builds/[build-slug]/
Artefacts:
  - PRD.md
  - SDD.md
  - /jsx/ (3 files, see manifest)

[Optional context: this is a v2 of an existing product, or this is trading infra, 
 or this is mobile-first, etc.]

Please break this down into tickets and route to the desks.
```

The PM takes it from there.

---

## What Happens Next

**Within 10–30 minutes (depends on build size):**

- PM reads PRD + SDD + JSX
- PM breaks into tickets: each independently testable, each with acceptance criteria
- PM posts ticket summary to `sprint_log` and messages you: "X tickets generated, routed to desks. Starting planning phase."

**Within hours:**

- Senior Advisors write execution plans per ticket
- Cross-desk coordination happens at this layer (API contracts, design specs, data requirements)
- Plans logged to `plans` table

**Hours to days (depends on build size):**

- Executors build per plan
- Stuck → escalate to Senior → unblock → continue
- PRs open as tickets complete
- Senior Advisor reviews PR against plan
- Senior QA reviews build against PRD
- QA + Functional Tester run unit/integration/e2e
- Merge when all gates green

**After each build closes:**

- PM writes post-mortem
- Reusable patterns logged to `skills_library`
- You get a build summary: what shipped, what broke, what the house learned

---

## Your Role During the Build

Minimal. The PM contacts you when:

- A PRD clause is ambiguous and the PM needs clarification
- A Senior Advisor flags PRD-drift and the PM wants you to confirm scope
- A GREEN/YELLOW/RED decision is needed on a trading strategy
- The build completes

You do **not** need to answer individual agent questions. All escalation flows through the PM.

---

## Trading Builds (PineScript desk + Backtester)

If the build includes indicators or trading strategies:

1. Hypothesis goes to Senior PineScript Dev (formalises indicator spec) or Senior Backtester (formalises hypothesis as experiment)
2. PineScript Developer implements on TradingView or Quantower
3. Indicator Tester verifies on live charts across declared timeframes/assets
4. Senior Backtester designs experiment: params, metrics, acceptance criteria, walk-forward
5. Backtester (pure Python) runs the parameter sweep
6. Senior Backtester synthesises results, produces GREEN/YELLOW/RED verdict
7. GREEN → production handoff notes for you to paper-trade or live-deploy

**Autoresearch loop:** if the Senior Backtester wants to tune a strategy, it designs a Karpathy-style parameter sweep with convergence criteria (<0.5% improvement over 3 iterations). The Backtester runs the loop until convergence.

---

## Example Handoff — Fade Bot Enhancement

```
New build.

Path: ~/software-house/builds/fade-bot-v2-rate-limit-handling/

Artefacts:
  - PRD.md       — add rate-limit aware retry logic + circuit breaker
  - SDD.md       — uses existing Fade Bot architecture (RADAR→PULSE→EDGE→CORE→STRIKER), 
                   new component in CORE, adjustments to STRIKER
  - /jsx/        — none (backend-only build)

Context: this is backend-only, existing AWS eu-west-1 deploy. Don't touch 
the latency path — sub-1ms is already tight. Rate-limit logic should trigger 
in CORE before STRIKER fires.

Please break this down into tickets.
```

PM response (expected):

```
Received. Reading PRD + SDD.

Initial ticket plan:
  T-001 — CORE: add RateLimitGuard module with token-bucket tracker
  T-002 — CORE: integrate RateLimitGuard into decision path
  T-003 — STRIKER: accept skip-signal from CORE on rate-limit hit
  T-004 — DevOps: CloudWatch metric for rate-limit trips
  T-005 — QA: regression on sub-1ms latency path (critical — must not degrade)

Routing:
  T-001, T-002, T-003 → Senior Backend Dev
  T-004 → Senior DevOps
  T-005 → Senior QA

Senior DevOps will post an advisory memo on AWS rate-limit budgets before 
Senior Backend Dev starts T-001.

Planning phase starts now. Will ping when plans are ready for review.
```

---

## Three Things to Remember

1. **Don't skip the JSX.** Even a rough draft anchors the front-end desks. Pure PRD-to-code produces uglier output.
2. **Don't fragment the handoff.** Give the PM all three artefacts at once. Piecemeal input breaks the planning loop.
3. **Let the house finish.** The build isn't done when code ships — it's done when the post-mortem lands in `skills_library`. That's where compounding lives.
