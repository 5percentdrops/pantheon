# Universal Engineering Escalation

## Purpose
The Jack/Marcus escalation pattern is not exclusive to backend work.

It applies to every Software House engineering lane:
- backend
- frontend
- mobile
- TradingView / Pine Script
- Quantower / C#
- DevOps
- QA/test engineering
- future specialist engineering roles

## Universal pattern

```txt
Standard developer executes assigned task
→ if blocked, standard developer gets 7-10 self-fix attempts
→ if still blocked, standard developer sends blocker packet to senior developer
→ senior developer gets 3 diagnosis/fix cycles
→ if still blocked, senior developer escalates to Arthur
→ Arthur sends:
   A. code packet to Cody
   B. approach packet to Magnus
→ Cody reports code-level findings to Arthur
→ Magnus reports approach-level findings to Arthur
→ Arthur chooses route
→ Arthur sends selected route to relevant senior developer
→ senior developer rewrites plan/checklist
→ standard developer resumes sequential execution
```

## Hard rules
- Magnus is the only Principal-level escalation agent.
- Cody and Magnus are available to all engineering lanes.
- Standard developers do not route directly to Cody or Magnus.
- Senior developers escalate through Arthur.
- Arthur routes the selected solution back to the relevant senior developer, not directly to the standard developer.
