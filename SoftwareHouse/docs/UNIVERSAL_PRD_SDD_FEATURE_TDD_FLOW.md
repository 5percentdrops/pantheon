# Universal PRD → SDD → Feature Tickets → Task-Level Superpowers TDD Flow

## Scope
This applies to every Software House engineering lane:

- Backend
- Frontend
- Mobile
- TradingView / Pine Script
- Quantower / C#
- DevOps
- QA / test engineering
- future specialist engineering roles

## Universal flow

```txt
Approved PRD
→ Arthur classifies technical domain
→ Arthur routes to relevant senior owner
→ senior owner converts PRD into lane-specific SDD
→ senior owner breaks SDD into feature tickets
→ senior owner breaks every feature ticket into task blocks
→ senior owner writes Superpowers-style task-level TDD
→ standard developer executes one task at a time
→ task test is red first
→ developer implements
→ task test passes green
→ only then move to next task
→ feature complete
→ PR submitted
→ GitHub checks green
→ required review approval received
→ merge
```

## Senior owner responsibilities

Every senior owner must create:

```txt
SDD.md
FEATURE_TICKETS.md
TASK_TDD_PLAN.md
CHECKLIST.md
ASSIGNMENT_PACKET.md
```

Each task block must include:

- task ID
- objective
- files to touch
- red test / failing check
- green implementation target / passing check
- exact steps
- acceptance criteria
- task green criteria
- PR green criteria
- rollback notes if needed

## Standard developer responsibilities

Every standard developer must:

1. Execute only the current assigned task.
2. Prove the red/failing check first.
3. Implement only what is needed to pass.
4. Run the green/passing check.
5. Stop and report status.
6. Move to the next task only after current task is green.
7. Never merge unless the GitHub PR is green and approved.

## Hard rules

```txt
No task red/green TDD
→ no implementation

No current task green
→ no next task

No GitHub PR green + required approval
→ no merge
```
