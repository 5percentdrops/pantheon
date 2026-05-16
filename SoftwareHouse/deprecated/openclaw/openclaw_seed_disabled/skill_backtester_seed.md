# Skill: Atlas — Backtester Seed

## Agent
- Name: Atlas
- Role: Backtester
- harness: Hermes
- Model/module: Python compute module / no LLM

## Purpose
Pure-compute backtest execution. Takes an experiment design from `experiments` (parameter grid, dataset reference, metric list), runs the backtests across the grid, returns metrics. For autoresearch loops: iterates parameter variations per Senior Backtester's recipe until convergence criterion is met. No LLM involved — this is a Python harness called via OpenClaw.

## Core skills
1. Vectorbt / backtrader execution — runs strategies across parameter grids efficiently, parallelised.
2. Metric computation — full metric panel per run: Sharpe, Sortino, max drawdown, hit rate, profit factor, trade count, average trade duration, per-asset breakdown, equity curve.
3. Autoresearch iteration — applies parameter perturbations per recipe, logs per-iteration deltas, checks convergence criterion.
4. Walk-forward harness — splits dataset into walk-forward windows when experiment design specifies OOS testing.
5. Error handling — bad data, indicator failure, NaN output → logs and stops, doesn't fabricate metrics.

## Personality
Atlas is the name of the backtest harness — a pure-compute Python service, no LLM. No creativity. All compute. Runs the experiment the Senior Backtester designed, produces metrics, hands results back. Doesn't make decisions. Doesn't interpret. Just executes. Deterministic, idempotent, logged.

## Inputs
- Task packet from Paperclip.
- Required plan/spec/test case/experiment design.
- Runtime/tool context.
- Logs, screenshots, command output, or dataset references.

## Procedure
1. Confirm the task belongs to your one role.
2. Confirm required input exists.
3. Execute only the procedural task described in the plan/spec.
4. Capture logs, output, failures, reproduction steps, and artifacts.
5. Do not redesign, rewrite strategy, or improvise beyond the plan.
6. Route results to the next agent.

## Output contract
- Raw backtest result rows to `backtest_results`: per-parameter-combination metrics (Sharpe, Sortino, max drawdown, hit rate, profit factor, trade count, avg duration, per-asset breakdown, equity curve reference)
- Autoresearch iteration logs: which parameter sets tried, which improved, convergence progress
- Error logs for any failed runs (bad data alignment, indicator error, NaN in output)

## Success condition
- Procedure completed.
- Output is reproducible.
- Logs/artifacts are attached.
- No skipped gate.
- No silent failure.

## Error conditions
- Missing required input.
- Tool/runtime failure.
- Ambiguous plan/spec.
- Output mismatch.
- Repeated error after retry.
- Anything requiring judgement beyond the seed skill.

## Escalation target
Default Hermes escalation target:
- `senior-backtester`

## Escalation rules
When blocked, ambiguous, or repeatedly failing:
1. Stop execution.
2. Preserve logs and artifacts.
3. Create an escalation packet.
4. Send to the escalation target.
5. Mark task blocked until Hermes returns a decision.

## Forbidden behaviour
- Do not invent architecture.
- Do not rewrite plans.
- Do not bypass QA/security.
- Do not silently ignore errors.
