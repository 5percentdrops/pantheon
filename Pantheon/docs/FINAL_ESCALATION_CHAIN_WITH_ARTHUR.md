# Final Escalation Chain With Arthur

## Attempt budgets

| Agent | Role | Attempts |
|---|---|---:|
| Jack | Backend Developer | 15 self-fix attempts |
| Marcus | Senior Backend Developer | 3 solution attempts |
| Maxwell | Staff Escalation Engineer | 2 solution attempts |
| Cody | Senior Code Quality & Defect Review Engineer | 1 code-review pass |
| Magnus | Principal Engineer / Principal Solution Architect | approach review |

## Routing rule
All movement between levels is controlled by Arthur.

## Success rule
If Jack successfully implements any returned solution, Jack continues.

## Failure rule
If a returned solution fails and the current layer has attempts left, Arthur routes back to the same layer.
If no attempts remain, Arthur routes up to the next layer.
