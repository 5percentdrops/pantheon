# Error Learning Log Workflow

## Purpose
When a developer hits an error and cannot fix it after the allowed attempts, the error and its solutions must be captured in the wiki so the organisation learns.

## Flow

```txt
Standard developer hits error
→ self-fix up to 10 attempts
→ if unresolved, send ERROR_ESCALATION_PACKET.md to senior owner
→ senior owner first logs original error in wiki/errors/
→ senior owner gives Solution Attempt 1
→ standard developer tries it
→ result is logged as WORKED or FAILED

If failed:
→ senior gives Solution Attempt 2
→ result logged

If failed again:
→ senior gives Solution Attempt 3
→ result logged

If still unresolved after 3 senior attempts:
→ escalate through Arthur to Cody/Magnus
```

## Required log contents
1. Original error
2. Context
3. Developer self-fix attempts
4. Senior solution attempts
5. Result of each solution attempt
6. Which solution WORKED
7. Final status

## Folder

```txt
wiki/errors/
```
