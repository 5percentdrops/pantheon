# Final Engineer Escalation Policy

## Rule
Every higher-level solution must return to the standard developer first.

## Backend canonical flow

```txt
Jack 15 attempts
→ Marcus 3 attempts, each returned to Jack
→ Maxwell 2 attempts, each returned to Jack
→ Cody 1 code-review pass, returned to Jack
→ Magnus if Jack still cannot resolve after Cody
```

## Cody scope
Cody reviews:
- bugs
- security issues
- breaks / regressions
- failing tests
- runtime errors
- dependency/config issues
- misimplementations
- missing code
- any code-wise blocker

## Magnus scope
Magnus reviews:
- approach
- architecture
- route
- API/data-source choice
- library choice
- scalability
- reliability
- strategy

## Hard rules
- Jack has 15 self-fix attempts.
- Marcus has 3 solution attempts.
- Maxwell has 2 solution attempts.
- Cody returns to Jack first.
- Magnus comes only after Cody's guidance fails with Jack.
- All steps are logged in `wiki/errors/`.
