# Model Route Override Lifecycle Policy V8.2

Model route overrides are Paperclip issues and must validate against:

```text
SoftwareHouse/contracts/model_route_override_request.schema.json
```

## Storage

```text
SoftwareHouse/workspace/08_Model_Route_Overrides/
```

## Rules

1. Overrides cannot bypass budget policy.
2. Overrides cannot bypass human approval.
3. Overrides must name target agent, current model, requested model, reason, and budget impact.
4. Arthur's default remains `openai/gpt-5-mini` unless a board-approved governance change is merged.
