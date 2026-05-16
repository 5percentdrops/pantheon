# Caveman Full + Error Escalation Rules

## Summary

Every Software House agent uses Caveman full version by default.

Only one thing is exempt:

```text
Arthur's raw escalation error extract.
```

The raw error extract must stay raw so the Senior Developer can diagnose the real compiler/runtime failure.

## Required Flow

```text
Junior fails attempts 1–12
→ Arthur executes Context Shredder
→ Arthur writes sub-50-line failure summary
→ Arthur extracts RTK 150-head/150-tail final error
→ Arthur labels raw error extract as Caveman exception
→ Arthur hands packet to assigned Senior Developer
```

## Required Arthur Senior Handoff

Arthur must hand over:

```text
Feature Ticket
Red Test
SDD path
Project repo path
50-line max failure summary
Junior root cause, max 3 lines
Files changed
RTK 150/150 final error extract
Missing-data warning if needed
```

## Missing Error Rule

If the error is missing, Arthur still escalates.

```text
Do not block escalation because the error packet is imperfect.
Send what exists to the Senior Developer.
```

## Why

Senior Developers need exact errors.  
Caveman simplification is useful for agent discipline, but raw compiler/runtime errors must stay intact.
