# Software House — End-to-End Flow

21 agents across 9 desks: Governance · Backend · Frontend · Mobile · Mobile Design · DevOps · PineScript · QA · Data.

This document traces the life of a build from PRD intake through production ship.

---

## Phase 0 — Upstream (You, the Product Owner)

Everything before the house starts happens in your design environment. You use ChatGPT / Claude / Stitch / ChatGPT Image to produce three artefacts:

```
  Idea  →  PRD  ↔  JSX front-end draft  →  SDD
  (you iterate these with whatever tools you like)
  
  ↓
  
  Hand to Project Manager: PRD + SDD + JSX
```

By the time work hits the house, the design is drafted. The house productionises it — it doesn't do the original design work.

---

## Phase 1 — Ticket Generation (Governance)

```
  You ──►  PROJECT-MANAGER  ──►  tickets table
           (Hermes, Opus 4.7)
              │
              ├──►  ticket breakdown: id, title, acceptance criteria,
              │     owner desk, priority, dependencies
              │
              └──►  sprint_log entry: "build started"
```

The PM reads the PRD, SDD, and JSX. Produces tickets — each independently testable, each assigned to a desk. You can optionally pre-write tickets yourself; the PM accepts them.

**Gate:** No ticket without acceptance criteria. The PM rejects vague tickets back to the user.

---

## Phase 2 — Planning (Per-Desk)

Each ticket routes to its desk's Senior Advisor. The Advisor writes the execution plan.

```
  ticket ──►  SENIOR-[DESK]-DEV          (Hermes, Opus 4.7)
                │
                ├──►  plans table (execution plan)
                │     - file structure / component tree / indicator spec
                │     - function signatures / props / parameters
                │     - test approach / acceptance criteria
                │     - handoff to executor
                │
                └──►  skills_library consult (reuse prior patterns)
```

**Cross-desk coordination happens at this layer:**

- Senior Backend Dev ↔ Senior Frontend Dev: API contracts before either builds
- Senior DevOps → proactive advisory to all desks (Hyperliquid proximity, AWS strategy, latency budgets)
- Senior PineScript Dev ↔ Senior Backtester: hypothesis formalisation + experiment feasibility
- Senior PineScript Dev ↔ Senior Data Analyst: data availability + feeds
- Senior Backtester ↔ Senior Data Analyst: dataset requirements for experiments

**Gate:** No executor starts without a plan. Plan drift = PR rejection.

---

## Phase 3 — Execution (Per-Desk)

Executor takes the plan, builds, opens PR.

```
  plan  ──►  [DESK]-DEV                    (Hermes, mix of Opus 4.6 / Sonnet 4.6 / Kimi / Haiku)
              │
              ├──►  code / designs / configs / indicators / data pipelines
              │
              ├──►  tests written alongside
              │
              └──►  PR open → review loop
                         │
                         └── stuck? ──►  back to Senior for unblock
```

**Escalation loop:** Executor stuck → specific escalation to Senior ("tried X, got Y, asking because Z") → Senior diagnoses → Executor continues. Senior never writes code for the Executor — gives direction.

**OpenClaw usage:** Executors use OpenClaw for mechanical work throughout this phase — running tests, deploying to staging, calling third-party APIs (ChatGPT Image, Google Stitch, Fastlane, Terraform, etc.). OpenClaw is the hands; the Executor is the brain.

---

## Phase 4 — Review (Per-Desk + Cross-Desk)

```
  PR ──►  SENIOR-[DESK]-DEV  (intent review — does code match plan?)
            │
            └── approve ──►  SENIOR-QA  (PRD review — does build meet requirement?)
                               │
                               ├── unit/integration tests ──►  QA         (Kimi K2.5)
                               │
                               └── functional tests ────────►  FUNCTIONAL-TESTER  (Kimi K2.5 + Playwright MCP)
                                                                │
                                                                └── tests live staging:
                                                                    - user journeys
                                                                    - FE/BE integration
                                                                    - order submission
                                                                    - third-party integrations
```

**Two-layer review:**

1. **Senior Advisor review** — does the code match the plan I wrote?
2. **Senior QA review** — does the build satisfy the PRD clause?

Both must pass. Senior QA flags PRD-drift to PM when the Senior Advisor approved something that doesn't meet the PRD.

**Gate:** Every PRD clause has a pass/fail. Mostly passing = failing.

---

## Phase 5 — Trading / Indicator Path (Specialised)

When the build includes trading indicators:

```
  hypothesis (from PM or Senior Backtester)
        │
        ▼
  SENIOR-PINESCRIPT-DEV  ──►  indicator_specs table (formalised spec)
        │
        ├──►  PINESCRIPT-DEV      (Opus 4.6, implements Pine / C#)
        │        │
        │        ▼
        │     INDICATOR-TESTER    (Kimi K2.5, verifies on live charts)
        │        │
        │        └──►  sign-off or failures back to dev
        │
        └──►  spec also routed to SENIOR-BACKTESTER
                 │
                 ▼
              experiments table (design: params, metrics, stopping rule)
                 │
                 ▼
              BACKTESTER  (pure Python, no LLM, OpenClaw runtime)
                 │
                 ▼
              backtest_results table (full metric panel per run)
                 │
                 ▼
              SENIOR-BACKTESTER synthesis  ──►  GREEN / YELLOW / RED verdict
                 │                                    │
                 │                                    └── GREEN → production handoff notes
                 ▼
              Karpathy autoresearch loop
              (iterate params until convergence
               <0.5% improvement × 3 iterations)
```

**Gate before GREEN:** walk-forward or out-of-sample validation required. In-sample-only = RED by default.

---

## Phase 6 — Deploy (DevOps)

```
  merged PR  ──►  SENIOR-DEVOPS  (plan reviewed)
                     │
                     ▼
                  DEVOPS-DEV  (Haiku 4.5, executes via OpenClaw)
                     │
                     ├── terraform plan → terraform apply
                     ├── GitHub Actions CI/CD
                     ├── Fastlane for mobile builds
                     ├── secrets via secret store
                     └── rollback path rehearsed in staging
                     │
                     ▼
                  FUNCTIONAL-TESTER  (post-deploy smoke test)
                     │
                     └── incidents? ──► SENIOR-DEVOPS → runbook to skills_library
```

**Gate:** Rollback path exists in the plan. If rollback isn't documented, the deploy doesn't ship.

---

## Phase 7 — Close Out (Governance)

```
  all tickets closed
        │
        ▼
  PROJECT-MANAGER  ──►  post-mortem
        │
        ├──►  what worked → skills_library (reusable patterns)
        │
        ├──►  what failed → skills_library (failure modes to avoid)
        │
        └──►  sprint_log: "build complete"
              builds.status = 'complete'
              builds.post_mortem_id = <new entry>
```

**Gate:** A build cannot be marked complete until its post-mortem exists in `skills_library`. This enforces the learning loop — no post-mortem, no closure, no compounding.

---

## The Hermes Self-Learning Loop (Why It Compounds)

Every reasoning agent in the house runs on Hermes. Hermes maintains `skills_library` — a Supabase table where agents log reusable patterns, runbooks, failure modes, and recipes after every build.

```
  Build 1 ──►  patterns logged: 20
  Build 2 ──►  reuses 12, logs 18 new    (total: 38)
  Build 3 ──►  reuses 28, logs 15 new    (total: 53)
  ...
  Build 10 ──►  reuses 140, logs 8 new   (total: 220+)
```

The house gets sharper, faster, and cheaper with every build. By build 10, the Senior PineScript Dev isn't designing FVG detectors from scratch — it's composing from building blocks already proven in prior builds. The Senior DevOps isn't writing AWS setup from nothing — it's instantiating a pattern it wrote six builds ago.

This is the entire point of running on Hermes instead of OpenClaw for every reasoning role: **Hermes remembers**.

---

## Summary Gates

| # | Gate | Owner | Blocker if failed |
|---|---|---|---|
| 1 | Ticket has acceptance criteria | PM | Ticket rejected back to user |
| 2 | Executor has plan before coding | Senior Advisor | Executor escalates for plan |
| 3 | PR matches plan (intent review) | Senior Advisor | Request changes |
| 4 | Build meets every PRD clause | Senior QA | Build rejected to originating desk |
| 5 | Functional tests pass on staging | Functional Tester | Bug + retest cycle |
| 6 | Indicator spec verified on live charts | Indicator Tester | Spec clarification or rework |
| 7 | Backtest has walk-forward or OOS | Senior Backtester | RED verdict, no production |
| 8 | Deploy has rollback path | Senior DevOps | Deploy blocked |
| 9 | Post-mortem logged before build close | PM | Build stays open |
