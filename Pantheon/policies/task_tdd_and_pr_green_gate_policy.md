# Task TDD and PR Green Gate Policy

## Task-level rule

Jack must execute tasks sequentially.

```txt
Task 1 TDD/checks must pass
→ then Jack may move to Task 2
```

Jack may not skip ahead, bundle future tasks, or merge partial work that has not passed its task-level TDD.

## Marcus responsibility

Marcus must provide, for every feature ticket:

1. Feature-level objective
2. Task-level blocks
3. TDD/red-green requirement for every task
4. Acceptance criteria for every task
5. PR green criteria for the feature/ticket
6. Merge criteria

## Jack responsibility

Jack must:

1. Execute only the current assigned task.
2. Run the task TDD/checks.
3. Mark the task green only after tests/checks pass.
4. Move to the next task only after current task is green.
5. Open/submit PR only when the feature/ticket is complete.
6. Merge only after the GitHub PR is green and approved by the configured review process.

## PR merge rule

```txt
No approved PR
→ no merge

No green GitHub checks
→ no merge

No task-level TDD pass
→ no next task
```

## Meaning of "green"

"Green" means:

- task-level TDD/checks pass for task progression
- GitHub PR checks pass for merge readiness
- required reviewer approval exists before merge
