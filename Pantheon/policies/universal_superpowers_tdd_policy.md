# Universal Superpowers TDD Policy

## Policy
Every senior engineering owner must use the Superpowers TDD skill when creating task-level plans.

## Required planning sequence

```txt
PRD
→ SDD
→ Feature Tickets
→ Task Blocks
→ Task-level TDD red/green checks
→ Assignment Packet
```

## Required execution sequence

```txt
Task red check fails
→ developer implements
→ task green check passes
→ move to next task
```

## Merge sequence

```txt
All task-level checks green
→ PR submitted
→ GitHub checks green
→ required approval received
→ merge
```

## Hard rules
- No task without TDD.
- No next task without green.
- No merge without GitHub green.
- No merge without required approval.
