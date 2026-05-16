# Arthur → Senior Escalation Handoff

## Header

- Project:
- Ticket ID:
- Assigned Senior:
- Attempt range failed:
- Route: Arthur → Assigned Senior Developer
- Handoff created at:

## Caveman Policy

```text
CAVEMAN_MODE: FULL
```

All summary and routing sections use Caveman full.

## Caveman Exception for Raw Error

```text
CAVEMAN_MODE: EXCEPTION
Reason: Raw error extract preserved for Senior Developer diagnosis.
```

## Required Paths

- PRD:
- SDD:
- Feature Ticket:
- Red Test:
- Project Repo:
- QA Log Folder:

## Sub-50-Line Failure Summary

> Maximum 50 lines. Clear, direct, no terminal spam.

## Junior Suspected Root Cause

> Maximum 3 lines.

## Files Changed Since Attempt 1

- 

## RTK Final Error Extract

```text
ERROR_EXTRACT_STATUS: COMPLETE | PARTIAL | MISSING
HEAD_LINES: 150
TAIL_LINES: 150
MIDDLE: STRIPPED
```

### Head — First 150 Lines

```text

```

### Tail — Last 150 Lines

```text

```

## Missing Data Warning

Use only if required:

```text
ERROR_EXTRACT_STATUS: INCOMPLETE
Action: Senior Developer must inspect repo/tests/logs directly.
```

## Senior Task

```text
Read this handoff, the original Feature Ticket, the matching Red Test, and the relevant SDD sections.
Provide a tactical fix to turn the test Green.
If the error extract is missing or incomplete, inspect the repo/tests/logs directly.
```
