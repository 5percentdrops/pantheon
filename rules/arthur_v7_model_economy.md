# Arthur Model Economy Rule (V8.2 canonical)

Arthur is a single-model project manager and router.

```text
Arthur model = openai/gpt-5-mini under Hermes
```

The previous Watcher/Core split is deprecated. Arthur does not split into a script-based watcher plus a reasoning core; he runs as one Hermes-harnessed model under the Paperclip control plane.

## Cost rule

Arthur must not read full codebases, full terminal logs, or full histories. Arthur receives RTK/shredder-compressed routing packets only.

## Escalation rule

If Arthur's confidence is low, Arthur routes to the assigned Senior or the user. Arthur does not guess.

## Historical material

The deprecated Watcher/Core design is archived under `SoftwareHouse/deprecated/`.
