# Error Memory Logging Ownership

## Folder

All error memory logs go into the same Obsidian-backed wiki folder:

```txt
wiki/errors/
```

Nothing else should be written in this folder except structured error-memory logs.

## Ownership

| Actor | Logging responsibility | File type |
|---|---|---|
| Jack / standard developer | Writes blocker after 15 failed self-fix attempts and records whether returned solutions WORKED or FAILED | BLOCKER_LOG |
| Marcus | Logs each senior solution attempt and its result | SOLUTION_LOG |
| Maxwell | Logs each Opus Max solution attempt and its result | SOLUTION_LOG |
| Cody | Logs code-level diagnosis, bug/security/code-quality findings, code fixes, and result | CODE_FIX_LOG |
| Magnus | Logs approach-level diagnosis, alternatives, route changes, and result | APPROACH_SOLUTION_LOG |
| Arthur | Enforces logging completeness before routing to the next escalation level | Governance |

## Protocol

```txt
Jack fails after 15 attempts
→ Jack writes BLOCKER_LOG
→ Arthur routes to Marcus

Marcus proposes solution
→ Marcus writes/updates SOLUTION_LOG
→ Arthur returns solution to Jack
→ Jack tests
→ result marked WORKED or FAILED

Maxwell proposes solution
→ Maxwell writes/updates SOLUTION_LOG
→ Arthur returns solution to Jack
→ Jack tests
→ result marked WORKED or FAILED

Cody reviews code
→ Cody writes CODE_FIX_LOG
→ Arthur returns guidance to Jack
→ Jack tests
→ result marked WORKED or FAILED

Magnus reviews approach
→ Magnus writes APPROACH_SOLUTION_LOG
→ Arthur routes approach back through relevant senior / Jack
→ result marked WORKED or FAILED
```

## Result labels

Use only:

```txt
WORKED
FAILED
PENDING
```

The solution that actually fixes the issue must be marked `WORKED`.

Failed attempts must remain in the log.
