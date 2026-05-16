# Obsidian Error Memory Protocol

## Purpose
`wiki/errors/` is the shared Obsidian-backed learning folder for Software House engineering failures and solutions.

It exists so future agents/developers can learn:

- what went wrong
- what failed
- what worked
- what to avoid next time
- what reusable fix should be repeated

## Single shared folder

```txt
wiki/errors/
```

All error memory logs go into this one folder.

Nothing else should be written into this folder except approved error-memory log files.

## Who writes to the folder

| Actor | What they write |
|---|---|
| Standard / junior developer | Blocker log after 10 failed self-fix attempts |
| Senior developer | Solution attempt logs, including failed and worked attempts |
| Cody | Code fix / bug diagnosis / patch result logs |
| Magnus | Approach solution / architecture route / alternative strategy logs |

## Required file types

Only these log types are allowed:

```txt
BLOCKER_LOG
SOLUTION_LOG
CODE_FIX_LOG
APPROACH_SOLUTION_LOG
```

## Core protocol

```txt
Standard developer fails after 10 attempts
→ writes BLOCKER_LOG in wiki/errors/
→ senior owner writes SOLUTION_LOG attempts in same folder
→ standard developer tests senior solution
→ result is logged as WORKED or FAILED
→ if Cody contributes a code fix, Cody writes CODE_FIX_LOG
→ if Magnus contributes an approach fix, Magnus writes APPROACH_SOLUTION_LOG
→ the solution that actually fixes the issue is marked WORKED
```

## Hard rules

- Do not delete failed attempts.
- Do not overwrite the original blocker.
- Do not create non-log notes in `wiki/errors/`.
- Do not split blocker and solution memory into separate folders.
- Mark the solution that fixed the issue as `WORKED`.
- Mark failed attempts as `FAILED`.
- Add reusable instructions so future builds avoid the same issue.


## Maxwell logging duty
If Maxwell provides Solution Attempt 1 or Solution Attempt 2, the attempts must be logged in `wiki/errors/`.

Allowed log type:
```txt
SOLUTION_LOG
```

If Maxwell's solution works, mark it:
```txt
WORKED
```

If both attempts fail, preserve both failed attempts and escalate to Cody.
