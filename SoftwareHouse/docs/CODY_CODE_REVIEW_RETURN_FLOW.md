# Cody Code Review Return Flow

## Purpose
Cody does not immediately send unresolved issues to Magnus.

Cody reviews the code and sends his findings back to the developer first.

## Correct flow

```txt
Maxwell fails 2 attempts
→ Arthur sends blocker to Cody
→ Cody reviews code

Cody checks:
- bugs
- security issues
- breaks / regressions
- failing tests
- missing implementation
- runtime errors
- dependency/config issues
- anything else code-wise that can make the code not work

Cody sends Code Review Return Packet back to Jack / relevant standard developer
→ developer attempts Cody's fix/review guidance

If developer fixes it:
→ mark Cody fix as WORKED
→ continue

If developer still cannot fix it:
→ developer sends Cody Review Failed Packet to Arthur
→ Arthur escalates to Magnus
```

## Hard rule
Magnus is not the immediate next step after Cody reviews.

Magnus is reached only when:
1. Cody has reviewed the code, and
2. Cody's review/fix has been returned to the developer, and
3. the developer still cannot resolve the issue, or
4. Cody explicitly identifies the issue as approach-level rather than code-level.
