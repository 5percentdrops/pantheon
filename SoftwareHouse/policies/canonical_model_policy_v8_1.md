# V8.1 Canonical Model Policy

## Source of truth

The canonical model field is `model` inside `SoftwareHouse/paperclip/organization.import.json`.

`llm_module` is display-only and must be derived from `model`.

## Canonical assignments

- Arthur: `openai/gpt-5-mini` under Hermes.
- Jack: `deepseek/deepseek-v4-pro` under Hermes.
- Marcus: `anthropic/claude-opus-4.7-xhigh` under Hermes.
- Maxwell: `anthropic/claude-opus-4.7-max` under Hermes.
- Cody: `openai/gpt-5.5` / latest Codex reviewer under Hermes.
- Magnus: `google/gemini-3.1-pro` under Hermes.
- Winston: `anthropic/claude-3.5-haiku` under Hermes.

Arthur single-model PM/head role language is deprecated. Arthur is single-model GPT-5 mini under Hermes unless a board-approved model route override exists.
