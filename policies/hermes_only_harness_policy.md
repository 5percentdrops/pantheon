# Hermes-Only Harness Policy

Every agent and every role in this repo uses Hermes as the harness.

OpenClaw must not be assigned as an agent harness.

OpenClaw may exist only as a broader installation/orchestration environment if needed; the agent harness field must be Hermes.

## V8 clarification

Hermes is the standard harness/runtime over the selected LLM model.

Paperclip is not a harness. Paperclip is the company/control plane.

OpenClaw is not an active standard agent harness in this package. It may exist as an optional external worker/environment, but V8 Paperclip employees use Hermes unless explicitly approved otherwise.
