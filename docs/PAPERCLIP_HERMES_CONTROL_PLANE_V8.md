# Software House V8 — Paperclip + Hermes Corrected Architecture

## Correct model

```text
Paperclip = company/control plane
Arthur = Project Manager / Head employee inside Paperclip
Hermes = harness/runtime over LLM models
LLM model = brain inside Hermes
Skills = reusable Hermes procedures
Memory = persistent/institutional context
Tools = shell/git/files/browser/MCP/API access
Paperclip issue = assigned job
Output contract = typed handoff format
Rubric/policy = quality gate
Human owner = board/final authority
```

## What changed from V7

V7 already had Arthur as head, Hermes-only harness, DeepSeek developers, Opus senior/staff escalation, Cody review, Magnus architecture, and Winston archive/memory.

V8 adds the explicit Paperclip company/control-plane layer:

- Paperclip owns goals, issues, budgets, heartbeats, audit and approvals.
- Arthur manages work inside Paperclip but is not Paperclip itself.
- Hermes is a harness/runtime, not the model.
- Every serious task starts with a context pack.
- Every handoff has a typed output contract.
- Budget and heartbeat policies are first-class.
- Memory hygiene becomes a scheduled Paperclip-governed routine.

## Patterns

### Pipeline

Used for normal delivery:

Context Pack -> PRD -> SDD -> Tickets -> TDD -> Implementation -> PR Review -> Merge Gate -> Memory Update

### Fan-out

Used for audits/red-team reviews:

Arthur splits work to Security, QA, Cody, Maxwell, Magnus, then synthesizes.

### Specialist Team

Used for architecture decisions:

Winston + Magnus + Marcus + Maxwell + Security review, then Arthur creates the decision packet.

## Safety

- No production trading keys in general workers.
- No code before tests.
- No tickets before architecture.
- No merge without green CI and review.
- No governance edits without approval.
- Execution cannot invent trades.
- Automated sizing must use fractional Kelly only.
