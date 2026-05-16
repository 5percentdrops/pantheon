# Arthur-Mediated Return Routing

## Purpose
Every higher-level engineering response must route through Arthur before returning to Jack or the relevant standard developer.

This applies to:
- Marcus
- Maxwell
- Cody
- Magnus

## Core rule

```txt
Higher-level agent
→ Arthur
→ Jack / relevant standard developer
```

No higher-level agent sends directly to Jack.

## If fixed, continue

The "if fixed, continue" rule applies to all escalation layers.

```txt
Marcus solution works
→ Jack continues

Maxwell solution works
→ Jack continues

Cody guidance works
→ Jack continues

Magnus approach route works
→ Jack continues / relevant senior updates plan if needed
```

## If not fixed

```txt
Returned solution fails
→ Jack reports result to Arthur
→ if that layer has attempts remaining, Arthur routes back to that layer
→ if that layer is exhausted, Arthur routes to next escalation layer
```

## Backend canonical chain

```txt
Jack 15 self-fix attempts
→ Arthur routes to Marcus

Marcus Attempt 1 → Arthur → Jack
Marcus Attempt 2 → Arthur → Jack
Marcus Attempt 3 → Arthur → Jack
→ if all fail, Arthur routes to Maxwell

Maxwell Attempt 1 → Arthur → Jack
Maxwell Attempt 2 → Arthur → Jack
→ if both fail, Arthur routes to Cody

Cody code review → Arthur → Jack
→ if Jack still cannot resolve, Arthur routes to Magnus

Magnus approach review → Arthur → relevant senior / Jack
```

## Magnus role
Magnus remains approach-focused.

Magnus checks:
- wrong approach
- alternative approaches
- architecture
- API/data-source route
- library choice
- scalability
- reliability
- security model
- implementation strategy
