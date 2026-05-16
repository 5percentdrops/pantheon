# Final Model Assignment Policy

## Harness
All roles use Hermes as the harness.

OpenClaw must not be assigned as an agent harness.

## Model map

| Tier | Model |
|---|---|
| Junior / Standard Developer | DeepSeek V4 Pro |
| Senior Developer | Opus 4.7 X High |
| Escalation Developer | Opus 4.7 Max |
| Principal Engineer | Gemini Pro 3.1 |

## Provider aliases

```yaml
junior_standard_dev:
  model: deepseek/deepseek-v4-pro
  harness: Hermes

senior_dev:
  model: anthropic/claude-opus-4.7
  reasoning_effort: x-high
  harness: Hermes

escalation_dev:
  model: anthropic/claude-opus-4.7
  reasoning_effort: max
  harness: Hermes

principal_engineer:
  model: google/gemini-3.1-pro
  harness: Hermes
```

## Note
Code reviewer roles, project managers, PRD research agents, and advisory roles remain on their own explicitly assigned models unless separately changed.
