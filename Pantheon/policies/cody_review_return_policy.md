# Cody Review Return Policy

## Rule
Cody sends code-review findings back to the standard developer first.

## Cody checks
Cody must check:
1. bugs
2. security issues
3. breaks / regressions
4. failing tests
5. runtime/config/dependency issues
6. missing implementation
7. anything else that can make the code not work

## After Cody review
The relevant standard developer must attempt Cody's fix/review guidance.

## If Cody guidance works
Mark the CODE_FIX_LOG as WORKED.

## If Cody guidance fails
The developer sends a Cody Review Failed Packet to Arthur.

Arthur then escalates to Magnus.

## Hard rule
Do not send to Magnus until the Cody review has been attempted by the developer, unless Cody explicitly states the issue is approach-level.
