# Arthur Single-Model Policy — GPT-5 Mini

## Decision

Arthur is now a single model again.

```text
Arthur = GPT-5 mini under Hermes
```

No separate Arthur single-model PM/head role is required for the default operating mode.

## Reason

Arthur model: GPT-5 mini under Hermes.

GPT-5 mini is selected because Arthur needs structured orchestration, not expensive senior architecture reasoning.

Arthur must reliably handle PRD intake, `[Project_Title]` extraction, namespace validation, domain classification, senior assignment, active ticket selection, attempt counting, escalation routing, `MASTER_STATUS.md` updates, merge-gate enforcement, and Winston archive handoff.

## Cost Control Rule

Arthur must not read full logs or whole codebases by default.

Arthur receives namespaced file paths, status rows, ticket IDs, Cody pass/fail logs, Context Shredder summaries, 150/150 final error extracts, and commit readiness packets.

Arthur does not receive full terminal history, unrelated project files, entire source trees, full retry traces, or uncompressed logs.

## Escalation Rule

If Arthur confidence is low:

```text
Arthur must route to the assigned Senior or user instead of guessing.
```

## Merge Rule

Arthur may gate a merge but must not silently auto-merge to main.

Default:

```text
Commit = Senior
PR = Senior
Merge = Arthur-gated or user-gated
```

## Forbidden

Arthur must not run as OpenClaw harness, replace Hermes, bypass the Senior final review, allow Junior to commit final project history, merge to main without gate conditions, or route across project namespaces.
