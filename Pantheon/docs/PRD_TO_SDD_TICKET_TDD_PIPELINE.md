# PRD → SDD → Feature Tickets → Task-Level TDD Pipeline

## Purpose
An approved PRD must be converted into an executable engineering pipeline before Jack writes code.

## Flow

```txt
User approves PRD
→ Arthur receives approval
→ Arthur routes approved PRD to Marcus
→ Marcus creates SDD.md
→ Marcus creates feature tickets
→ Marcus breaks each feature ticket into task-level checklist blocks
→ Marcus writes TDD/red-green tests for each task
→ Marcus assigns tasks to Jack
→ Jack executes task by task
→ current task must be green before next task
→ PR must be green before merge
```

## Revision loop

If user requests revision:

```txt
User revision request
→ Arthur
→ Arthur routes back to beginning of pipeline
→ research/feasibility/advisory loop restarts as required
```

## Approval rule

Arthur cannot kill a project unless the user explicitly says to stop.
Arthur cannot override user approval.
Once the user approves, Arthur routes forward.

## Marcus responsibilities

Marcus must create:

```txt
SDD.md
FEATURE_TICKETS.md
TASK_TDD_PLAN.md
CHECKLIST.md
JACK_ASSIGNMENT_PACKET.md
```

Every feature ticket must be broken into task blocks.

Every task block must include:
- objective
- files to touch
- exact steps
- red test
- green implementation target
- acceptance criteria
- PR/merge criteria
- rollback notes if needed

## Jack responsibilities

Jack must:
- execute only the assigned task
- run the task TDD
- get green before moving on
- create a blocker packet if stuck
- never skip ahead
