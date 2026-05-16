# Approval Flow — PM → Senior Advisor → Executor

Every ticket follows the same loop. Here's how the approvals and escalations work in practice.

---

## The Core Loop

```
┌─────────────┐  ticket   ┌─────────────────┐  plan   ┌────────────┐
│     PM      │  ───────► │ SENIOR ADVISOR  │ ──────► │  EXECUTOR  │
│ (Hermes PM) │           │  (Opus 4.7)     │         │   (mixed)  │
└─────────────┘           └─────────────────┘         └────────────┘
      ▲                            ▲                         │
      │                            │                         │
      │        escalation          │     stuck / blocked     │
      └────────────────────────────┴─────────────────────────┘
           (cross-desk blockers,     (code-level blockers,
            spec ambiguity,           missing library, etc.)
            scope change)
```

Escalation has two paths:

- **Executor → Senior Advisor** for code-level blockers. Most unblocks happen here.
- **Senior Advisor → PM** for cross-desk blockers (need input from another Senior) or scope/spec ambiguity (need user input).

---

## Stage 1 — Ticket Assignment

PM assigns a ticket to a desk. The ticket row carries:

- `ticket_id` — human-readable (T-042)
- `title` + `description`
- `acceptance_criteria` — the bar for "done"
- `owner_desk` — which desk owns it
- `priority` — 1 (urgent) to 5 (whenever)
- `dependencies` — other ticket_ids that must close first
- `status` — starts at `open`

PM sends a message to the desk's Senior Advisor. Status → `planning`.

---

## Stage 2 — Plan Writing

Senior Advisor reads the ticket, PRD clauses it implicates, and relevant skills_library entries. Writes the plan:

**Backend plan might include:** file structure, function signatures, DB schema changes, API contracts, error handling, test plan, definition of done.

**Frontend plan might include:** component tree, props interfaces, state ownership, responsive breakpoints, accessibility requirements, test plan.

**PineScript plan:** entry rules, exit rules, parameters (with defaults + bounds), alert conditions, plots, target platform, version.

**Backtest plan:** hypothesis, baseline params, parameter grid, metric list, acceptance criteria, multiple-testing correction, stopping rule.

Plan lands in `plans` table. Senior posts the plan to the Executor.

Status → `in-progress` when Executor acknowledges.

---

## Stage 3 — Execution

Executor reads plan, builds per plan, writes tests alongside code, opens PR.

**Rules:**
- Never deviate from the plan without a PR comment explaining why
- Never expand scope. Expansions go back to Senior for plan amendment
- Test alongside code, not after
- Use OpenClaw for mechanical work (running tests, deploying to staging, calling third-party APIs)

If stuck for more than 20 minutes, escalate. Don't keep guessing.

**Escalation template:**

> Stuck on [specific thing]. Tried [approach 1, approach 2]. Got [error / behaviour]. Docs say [X]. Asking because [the plan says Y but I'm seeing Z, or the library's behaviour contradicts the plan's assumption].

Senior Advisor responds with direction, not code. "Try using `request.security()` with lookahead=off — that's the Pine quirk here" not "here's the code, paste it in."

Status → `in-review` when PR opens.

---

## Stage 4 — Review (Two Layers)

### Layer 1: Senior Advisor review

Senior reads the PR against the plan they wrote. Three verdicts:

- **approve** — code matches plan, tests cover it, move to Senior QA
- **request-changes** — specific issues, Executor addresses, re-review
- **reject** — full rewrite, usually because of fundamental plan-drift

Plan drift gets cited: "PR uses Zustand; plan specified local state. Either revert to local state or write up why Zustand is needed and I'll amend the plan."

### Layer 2: Senior QA review

When Senior Advisor approves, the ticket moves to Senior QA. Senior QA reviews against **PRD intent**, not just plan:

- Does this ticket satisfy the PRD clauses it was supposed to cover?
- Are edge cases handled that the plan might not have enumerated?
- Is there silent drift from the PRD that the plan inherited?

Senior QA routes tests:

- **Unit + integration** → QA (Kimi K2.5)
- **End-to-end functional** → Functional Tester (Kimi K2.5 + Playwright MCP)

Status → `in-qa` while tests run.

---

## Stage 5 — Close Ticket

When QA passes on all layers:

- Ticket status → `done`
- `completed_at` set
- PR merged (squash or rebase per repo convention)
- Any reusable patterns discovered during this ticket logged to `skills_library` by the Senior Advisor or Executor

---

## Stage 6 — Close Build

When all tickets in a build are `done`:

- PM posts a build summary in Paperclip
- PM writes post-mortem to `skills_library` (what worked, what failed, what's reusable)
- `builds.status` → `complete`
- `builds.post_mortem_id` set
- User gets a summary message: "Build done. Shipped X. Caught Y bugs. Logged Z reusable patterns."

**Hard gate:** a build cannot close without its post-mortem in `skills_library`. This is what drives the learning loop.

---

## Escalation Scenarios

### Executor stuck on code

```
Executor ──► Senior Advisor
(specific escalation template, within 20 min of stuck)

Senior Advisor ──► Executor
(direction, not code, within 1 hour typically)
```

### Executor stuck, Senior also stuck

```
Executor ──► Senior Advisor
Senior Advisor ──► PM
PM ──► other Senior Advisor (if cross-desk help needed)
    OR ──► user (if scope/spec clarification needed)
```

### Senior Advisor flags PRD-drift

```
Senior QA reads a build, sees it doesn't match PRD clause X.
Senior QA ──► PM: "T-042 ships but PRD clause 3.2 says W, build does Y. 
                    Possible drift. User intent check?"
PM ──► user (confirm intent)
User ──► PM: "intended W, reject the build"
PM ──► Senior Advisor: "rework T-042 to match clause 3.2"
```

### Scope creep request from Executor

```
Executor: "while I was in here I noticed Z also needs fixing"
Executor ──► Senior Advisor: "flagging Z as a separate ticket candidate"
Senior Advisor ──► PM: "create T-XXX for Z, not adding to current ticket"
PM creates new ticket. Current ticket stays in scope.
```

---

## Anti-Patterns to Avoid

**Executor asks the user a question directly.** Never happens. All questions route through Senior Advisor → PM.

**Senior Advisor writes code for the Executor.** Corrupts the learning loop. Senior gives direction, Executor writes code.

**PM picks up a plan themselves.** PM doesn't plan, doesn't code, doesn't design. PM routes and unblocks.

**Skip post-mortem to save time.** Kills the compounding. Build stays open until post-mortem lands.

**Executor starts without a plan.** Plan drift starts here. Ticket goes back to the Senior.
