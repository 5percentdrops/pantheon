# Patch Notes V8.1

This patch applies the audit feedback from the V8 review.

## Fixed

1. Arthur model contradiction removed. Arthur is `openai/gpt-5-mini` under Hermes everywhere canonical.
2. Every imported agent now has a non-empty canonical `model` field.
3. `llm_module` is display-only and derived from `model`.
4. All schemas referenced by routes/pipelines resolve from `SoftwareHouse/contracts/`.
5. `prd.schema.json`, `heartbeat.schema.json`, `transcript.schema.json`, and `budget_event.schema.json` added.
6. Pipelines are wired into `event_routes`.
7. Clara dual-review route restored.
8. Budget caps no longer exceed the global monthly cap.
9. Active OpenClaw seed/policy files moved to deprecated history.
10. V8.1 validator now checks the things that previously false-passed.

## Still intentional

- `SoftwareHouse/schemas/` remains as a legacy mirror for compatibility.
- `SoftwareHouse/contracts/` is the canonical runtime/validation source.
- Paperclip and Hermes are not installed by this repo; this repo imports/stages org configuration.
