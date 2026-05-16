> V8.1 note: canonical Arthur model is `openai/gpt-5-mini` under Hermes. Older Watcher/Core or DeepSeek/Opus Arthur claims are deprecated.

# V7 Namespaced Pipeline Policy

## Required Keeps

The following V7.0 elements are retained:

1. Global workspace.
2. `[Project_Title]` namespace rule.
3. Strict SDD Alignment block.
4. Context Shredder.
5. 150/150 final error extraction.
6. Escalation pipeline.
7. Forensic report before architecture rethink.

## Required Changes

The following improvements are mandatory:

Arthur model: GPT-5 mini under Hermes.
2. Junior retries are capped at 12 before shredder escalation.
3. `06_Project_Repos/[Project_Title]/` is the deterministic home for actual code.
4. Stage 5 Finalization is mandatory after QA Pass.
5. Winston archives final artifacts and error lessons.
6. `MASTER_STATUS.md` uses a structured schema.
7. Senior owns commit to feature branch.
8. Merge remains gated.

## Model Economy Policy

Use expensive senior models only for SDD generation, ticket/test generation, architectural fixes, final commit review, and approach rethinks.

Use cheaper models/scripts for file watching, status checks, mechanical routing, junior implementation, retry loops, and summarizing logs after shredder.

Arthur model: GPT-5 mini under Hermes.

Default:

```text
Arthur = GPT-5 mini under Hermes
```

Allowed substitutions:

- Any cheaper reasoning model that passes `validate_v7_pipeline.py`.
- Any model approved in `rules/model_map.md`.
- Any local deterministic script for non-reasoning watcher tasks.

Not allowed:

- Arthur full routing on a pure flash model without validation.
- Arthur merging directly to main.
- Arthur bypassing Senior final review after QA Pass.

## Arthur Single-Model Update

```text
Arthur = GPT-5 mini under Hermes
```

Arthur is no longer split into Watcher/Core by default. Arthur remains a single manager/router/state-controller model. If confidence is low, Arthur routes to the assigned Senior or the user instead of guessing.
