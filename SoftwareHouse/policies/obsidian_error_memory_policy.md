# Obsidian Error Memory Policy

## Folder

```txt
wiki/errors/
```

This is a dedicated Obsidian wiki folder for error-learning logs.

## Allowed contents
Only error-memory log files are allowed.

Allowed log types:
- BLOCKER_LOG
- SOLUTION_LOG
- CODE_FIX_LOG
- APPROACH_SOLUTION_LOG

## Standard developer duty
After 10 failed self-fix attempts, the standard developer must create a BLOCKER_LOG.

## Senior developer duty
The senior developer must log every solution attempt.

If Solution Attempt 1 fails, keep it.
If Solution Attempt 2 works, mark Solution Attempt 2 as WORKED.
Do not delete failed attempts.

## Cody duty
If Cody diagnoses a bug, provides code, reviews a patch, or fixes a code-level issue, Cody must write a CODE_FIX_LOG.

## Magnus duty
If Magnus provides a new approach, architecture, data-source route, API route, or library route, Magnus must write an APPROACH_SOLUTION_LOG.

## Learning rule
Every log must include reusable instructions.
The point is to avoid repeating the same error in future builds.
