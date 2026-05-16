# Final Engineer Escalation Routine

## Purpose
This document defines the final Software House escalation routine for Jack and the wider engineering lanes.

The key rule:

```txt
Any solution from a higher-level agent goes back to the standard developer first.
```

For backend, the standard developer is Jack.

## Backend chain

```txt
Jack
→ Marcus
→ Maxwell
→ Cody
→ Jack attempts Cody guidance
→ Magnus if still unresolved
```

## Attempt budgets

| Stage | Agent | Official title | Attempts |
|---|---|---|---:|
| Standard developer | Jack | Backend Developer | 15 self-fix attempts |
| Senior developer | Marcus | Senior Backend Developer | 3 solution attempts |
| Staff escalation | Maxwell | Staff Escalation Engineer | 2 solution attempts |
| Code review | Cody | Senior Code Quality & Defect Review Engineer | 1 code-review pass |
| Principal approach review | Magnus | Principal Engineer / Principal Solution Architect | approach-level review |

## Detailed flow

```txt
1. Jack writes code according to Marcus's plan/checklist/TDD.
2. Jack hits an error.
3. Jack tries up to 15 self-fix attempts.
4. If Jack still cannot fix it, Jack sends blocker to Marcus.

5. Marcus reviews because Marcus wrote the plan.
6. Marcus gives Solution Attempt 1.
7. Solution goes back to Jack.
8. If Jack fixes it, stop.
9. If not, Marcus gives Solution Attempt 2.
10. Solution goes back to Jack.
11. If still not fixed, Marcus gives Solution Attempt 3.
12. Solution goes back to Jack.
13. If still not fixed, Arthur routes to Maxwell.

14. Maxwell gives Solution Attempt 1.
15. Solution goes back to Jack.
16. If not fixed, Maxwell gives Solution Attempt 2.
17. Solution goes back to Jack.
18. If still not fixed, Arthur routes to Cody.

19. Cody performs one code-review pass.
20. Cody checks bugs, security issues, breaks, regressions, failing tests, runtime errors, dependency/config issues, misimplementations, missing code, and code-wise blockers.
21. Cody sends Code Review Return Packet back to Jack.
22. Jack attempts Cody's guidance.
23. If Jack fixes it, stop.
24. If Jack still has the same issue, Arthur routes to Magnus.

25. Magnus reviews the approach, architecture, API/data-source choice, library choice, scalability, reliability, and strategy.
```

## Hard rules

- Jack gets 15 attempts, not 7-10.
- Marcus gets 3 attempts.
- Maxwell gets 2 attempts.
- Cody gets one code-review pass.
- Cody returns to Jack first.
- Magnus comes after Cody's guidance fails with Jack.
- No higher-level agent bypasses the standard developer.
- All blockers, solution attempts, code fixes, and approach fixes are logged into `wiki/errors/`.


## Arthur-mediated correction
Every returned solution from Marcus, Maxwell, Cody, or Magnus routes through Arthur first.

The solution does not go directly from the higher-level agent to Jack.

If Jack applies the returned solution and it works, Jack continues.
If it fails, Jack reports failure to Arthur and Arthur routes the next step.
