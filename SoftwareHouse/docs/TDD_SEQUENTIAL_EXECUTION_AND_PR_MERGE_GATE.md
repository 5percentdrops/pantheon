# TDD Sequential Execution and PR Merge Gate

## Correct sequence

```txt
Marcus creates SDD
→ Marcus creates feature tickets
→ Marcus breaks feature tickets into task blocks
→ Marcus writes TDD/red-green checks for each task
→ Jack executes Task 1
→ Task 1 TDD passes
→ Jack moves to Task 2
→ all tasks pass
→ Jack opens/submits PR
→ PR checks pass
→ reviewer approval received
→ Jack merges
```

## Important distinction

Task green and PR green are not the same.

| Gate | Meaning |
|---|---|
| Task green | Task-level TDD/checks pass. Jack may move to next task. |
| PR green | GitHub PR checks pass and review approval exists. Jack may merge. |

## Hard rules

- Jack does not move to the next task until the current task passes its TDD/checks.
- Jack does not merge until the GitHub PR is green and approved.
- Marcus must define TDD/checks for every task, not just every feature.
- Marcus must define PR green criteria for every feature/ticket.
