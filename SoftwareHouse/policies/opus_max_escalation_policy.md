# Opus Max Escalation Policy

## Rule
After a senior engineer fails 3 diagnosis/fix attempts, the blocker must go to Maxwell before Cody or Magnus.

## Maxwell role
Maxwell uses OPS / Opus 4.7 Max under Hermes.

## Attempt limit
Maxwell has 2 solution attempts.

## If Maxwell succeeds
The worked solution is logged as WORKED and the developer continues.

## If Maxwell fails both attempts
Escalate to Cody.

## Cody role
Cody checks whether anything is missing or wrong from a code-wise perspective.

## Magnus role
Magnus is reached after Cody confirms the code is fine, or Cody identifies that the real issue is approach/architecture/route rather than code.

## Hard rule
Do not skip Maxwell unless the user explicitly orders an immediate Cody/Magnus escalation.
