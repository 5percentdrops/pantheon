# Arthur Escalation Handoff Policy

## Trigger

Arthur creates an escalation handoff after the Junior fails the capped retry loop.

Current retry cap:

```text
Junior attempts = 1–12
```

## Required Arthur Handoff to Senior

Arthur must hand the escalation packet to the assigned Senior Developer.

The packet must include:

1. Original Feature Ticket path.
2. Matching Red Test path.
3. Project SDD path.
4. Project repo path.
5. Sub-50-line failure summary.
6. Junior suspected root cause, maximum 3 lines.
7. Files changed since attempt 1.
8. RTK error extract:
   - first 150 lines of final error
   - last 150 lines of final error
   - middle noise removed
9. Missing-data warning if any required item is unavailable.
10. Caveman exception label for the raw error extract.

## Senior Handoff Rule

Arthur must not simply save the escalation log.  
Arthur must route it to the assigned Senior Developer.

Required route:

```text
Arthur → Assigned Senior Developer
```

## Missing Error Rule

If the RTK error extract is missing, incomplete, corrupted, or unavailable:

```text
Arthur must send the available error material to the Senior Developer anyway.
```

Arthur must include this warning:

```text
ERROR_EXTRACT_STATUS: INCOMPLETE
Action: Senior Developer must inspect repo/tests/logs directly.
```

## Caveman Exception

The summary is Caveman full.

The raw error extract is not Caveman-compressed.

Required label:

```text
CAVEMAN_MODE: EXCEPTION
Reason: Raw error extract preserved for Senior Developer diagnosis.
```
