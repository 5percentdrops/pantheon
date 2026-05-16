# PR Green + Approval Merge Policy

A PR is mergeable only when:

1. Every task in the feature ticket has passed its task-level TDD/check.
2. Full feature/ticket checks pass.
3. GitHub PR checks are green.
4. Required reviewer approval exists.
5. There are no unresolved blockers.

If any item is false:

```txt
No merge.
```
