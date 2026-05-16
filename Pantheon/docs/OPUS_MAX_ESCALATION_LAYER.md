# Opus Max Escalation Layer

## Purpose
This adds a missing escalation step between senior developers and Cody/Magnus.

## Correct flow

```txt
Standard developer fails after 7-10 self-fix attempts
→ relevant senior developer gets 3 diagnosis/fix cycles
→ if senior fails all 3, escalate to Maxwell

Maxwell — Opus Max Escalation Engineer
→ Attempt 1
→ if WORKED, stop
→ if FAILED, Attempt 2
→ if WORKED, stop
→ if FAILED, escalate to Cody

Cody — Code Escalation Reviewer
→ checks code-wise issue
→ if code issue found, sends fix route back through Arthur/senior
→ if code is fine or approach is wrong, escalate to Magnus

Magnus — Principal Solution Architect
→ checks overall approach, architecture, API/data-source route, library choice, scalability, reliability
```

## Hard rules
- Maxwell has maximum 2 attempts.
- Cody is after Maxwell, not before Maxwell.
- Magnus is after Cody when the code is not the issue or the approach is suspect.
- Arthur controls routing.
- All attempts are logged into `wiki/errors/`.


## Cody return correction
After Maxwell fails twice, Cody reviews the code.

Cody does not immediately escalate to Magnus.

Cody sends Code Review Return Packet back to the standard developer first.

If the developer still cannot fix it after Cody's review, then Arthur escalates to Magnus.
