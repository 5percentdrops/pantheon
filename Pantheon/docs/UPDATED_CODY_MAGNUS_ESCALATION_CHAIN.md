# Updated Cody → Jack → Magnus Escalation Chain

## Chain

```txt
Standard developer
→ Senior developer
→ Maxwell / Opus Max
→ Cody / Code Review
→ Standard developer attempts Cody guidance
→ Magnus only if still unresolved
```

## Cody scope
Cody reviews:
- bugs
- security issues
- breaks
- regressions
- failing tests
- runtime errors
- dependency issues
- config issues
- missing implementation
- code-level blockers

## Developer after Cody
The developer must attempt Cody's returned guidance.

If it works:
```txt
mark WORKED
```

If it fails:
```txt
send Cody Review Failed Packet
→ Arthur
→ Magnus
```

## Magnus scope
Magnus reviews the approach, architecture, route, API/data-source choice, library choice, scalability, and reliability only after Cody's code-review path fails.
