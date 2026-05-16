# Cost Monitor Policy

`SoftwareHouse/company/budget_policy.yaml` is validated at install time.

Runtime cost enforcement must be wired in Paperclip/Hermes using `budget_event.schema.json`.

V8.1 prevents a known false-pass class by checking:
- per-agent caps exist;
- total per-agent caps are not above the global monthly cap;
- retry policy is labelled runtime retry only, separate from engineering escalation.
