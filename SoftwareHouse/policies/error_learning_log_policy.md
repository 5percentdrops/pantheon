# Error Learning Log Policy

## Standard developer rule
A standard developer gets 10 self-fix attempts.

If unresolved:
- stop
- create ERROR_ESCALATION_PACKET.md
- send it to the relevant senior owner

## Senior developer rule
The senior developer gets 3 solution attempts.

Before giving Solution Attempt 1, the senior developer must log the original error into:

```txt
wiki/errors/
```

Each senior solution attempt must be logged.

## Result labels
Use:

```txt
WORKED
FAILED
```

The working solution must be marked WORKED.
Failed attempts must stay in the log.

## If 3 senior attempts fail
Escalate through Arthur to Cody/Magnus.
