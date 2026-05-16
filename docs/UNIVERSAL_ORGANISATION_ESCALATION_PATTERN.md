# Universal Organisation Escalation Pattern

## Purpose
The Software House escalation routine applies across every organisation.

Each organisation adapts the same pattern to its own standard agents, senior owners, reviewers, and principal/approach reviewers.

## Canonical flow

```txt
Standard agent / standard developer
→ 15 self-fix attempts
→ router/project manager routes to relevant senior owner

Senior owner
→ 3 solution attempts
→ each solution routes through router/project manager back to the standard agent
→ if WORKED, standard agent continues
→ if all 3 fail, router routes to Maxwell

Maxwell — Staff Escalation Engineer
→ 2 solution attempts
→ each solution routes through router/project manager back to the standard agent
→ if WORKED, standard agent continues
→ if both fail, router routes to Cody/code reviewer

Cody / code-quality reviewer
→ one code/review pass
→ routes through router/project manager back to standard agent
→ if WORKED, standard agent continues
→ if FAILED, router routes to Magnus/principal engineer

Magnus / principal engineer
→ approach-level review
→ alternative approaches/routes
→ routes through router/project manager back to relevant senior and standard agent
```

## Core rule
No higher-level agent sends directly to the standard agent.

Everything routes through the organisation router/project manager.

## Success rule
If the standard agent applies a returned solution and it works, the standard agent continues.

## Failure rule
If the returned solution fails, the router/project manager routes back to the same layer if attempts remain, or to the next layer if attempts are exhausted.
