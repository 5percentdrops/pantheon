# Software House V8.0 — One-Click Install

## Install

```bash
bash scripts/one_click_install.sh
```

## Correct architecture

```text
Paperclip = company/control plane
Arthur = Project Manager / Head employee
Hermes = harness/runtime over LLM models
LLM model = GPT-5 mini / GPT-5.5 / Opus / Gemini / DeepSeek etc.
```

## What the installer does

1. Creates/validates V7 workspace folders.
2. Creates `workspace/MASTER_STATUS.md` if missing.
3. Validates the original V7 namespaced pipeline.
4. Validates Arthur single-model GPT-5 mini policy.
5. Validates the V8 Paperclip control-plane layer.
6. Validates universal typed handoff contracts.
7. Renders the Paperclip company import payload.
8. Stages `.stage/paperclip_company.import.json`.

## Core Rules

- Paperclip owns org/goals/issues/budgets/heartbeats/audit/approval gates.
- Arthur manages work inside Paperclip.
- Hermes is the only standard harness.
- Hermes sits on top of the selected LLM model.
- RTK is terminal/output compression only, never a harness.
- Context pack before serious work.
- Architecture before tickets.
- Tests before code.
- Junior attempts are capped.
- Senior owns commit.
- Merge remains gated.
- Winston archives final artifacts and real error lessons.
- Governance changes require human approval.
- No production trading API keys inside general agents.
- Execution cannot invent trades.
- Automated sizing must use fractional Kelly only.


## V8.1 integrity patch

V8.1 fixes the V8 audit issues:

- `model` is now the canonical model field.
- Arthur is collapsed to `openai/gpt-5-mini` under Hermes.
- `llm_module` is display-only and derived from `model`.
- `SoftwareHouse/contracts/` is the canonical schema directory.
- Routes and pipelines are validated against contracts.
- Pipelines are dispatchable through `event_routes`.
- Context-pack-first is validated structurally.
- OpenClaw active harness/seed material is disabled and moved to deprecated history.
- Budget caps are sanity-checked.
