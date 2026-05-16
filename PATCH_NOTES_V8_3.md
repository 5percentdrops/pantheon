# V8.3 Patch Notes

This patch applies the V8.2 audit corrections.

## Fixed (Arthur model contradiction, fourth round)

1. **Arthur agent `description` field** in all four agent-record files (`organization.import.json`, `agents.json`, `paperclip_company.import.json`, `.stage/paperclip_company.import.json`) — replaced "Arthur uses Sonnet 4.6 under Hermes." with "Arthur uses GPT-5 mini under Hermes."
2. **Arthur seed skill model line** (`SoftwareHouse/skills/hermes_seed/skill_arthur-project-manager_seed.md`) — replaced "OPS 4.7 under Hermes." with "openai/gpt-5-mini under Hermes." on the `## Model` line.
3. **Second Arthur seed file** (`SoftwareHouse/skills/hermes_seed/skill_project-manager_seed.md`) — replaced "Model/module: claude-opus-4-7" with "Model/module: openai/gpt-5-mini (display: GPT-5 mini under Hermes)".

## Fixed (Owen / synthetic model identifiers)

4. **Owen `personality` field** was copied from Atlas (a backtest harness). Replaced with role-appropriate text describing Owen as a research librarian.
5. **Owen `model` field** changed from `manual/notebooklm-workflow` (synthetic) to explicit `null` with `model_unassigned_reason` documenting the dependency on NotebookLM (a product, not an API model).

## Fixed (missing pipelines)

6. **`SoftwareHouse/pipelines/model_route_override_pipeline.yaml`** created. Was referenced by `event_routes.model_route_override_requested` but the file didn't exist.
7. **`SoftwareHouse/pipelines/audit_logging_pipeline.yaml`** created. Was referenced by `event_routes.agent_heartbeat`.

## Fixed (model identifier format)

8. **`anthropic/claude-opus-4.7-xhigh` and `anthropic/claude-opus-4.7-max`** — `xhigh` and `max` are Anthropic `effort` parameters, not part of the model name. Split into `model: anthropic/claude-opus-4.7` + `effort: xhigh|max` for 12 agents across all four agent-record files (11 senior-tier + Maxwell).

## Fixed (self-negating docs)

9. **`docs/V7_NAMESPACED_AUTONOMOUS_PIPELINE.md`** — stripped the "Arthur Watcher" / "Arthur Core" rows from the squad table and replaced the stapled "Arthur Single-Model Update" override with a single canonical paragraph.
10. **`rules/arthur_v7_model_economy.md`** — full rewrite. Old Watcher/Core narrative deleted.
11. **`prompts/V7_STAGE_PROMPTS.md`** — Stage 1 owner attribution corrected ("Arthur (single-model)" instead of "Arthur Watcher + Arthur Core"). The "Default Arthur Core model: DeepSeek V4 Pro" line and the stapled override section removed.

## Fixed (retry ladder cleanup)

12. **`schemas/v7_pipeline_config.schema.json`** — replaced V7 retry numbers as schema constants with a deprecation pointer to `engineering_escalation_ladder_v8_2.json`.
13. **`manifest.json.universal_engineering_escalation`** — stripped `standard_attempts` and `senior_attempts` numeric fields; added `canonical_source` pointer.

## Fixed (orphan harness)

14. **`SoftwareHouse/harnesses/codex_repo_worker.yaml`** moved to `SoftwareHouse/deprecated/harnesses/`. No active agent uses it; keeping it in `harnesses/` advertises a runtime that doesn't exist.

## Added

15. **`scripts/validate_arthur_consistency.py`** — structural check, not a string list. Enumerates every surface where Arthur's model can be stated (agent record fields, hermes_runtime, rules block, seed skill model declarations, doc/policy lines) and asserts they all normalize to canonical. Skips lines that are deprecation notices or multi-agent prose where Arthur is mentioned alongside another agent's model.
16. **`scripts/validate_event_route_pipelines.py`** — asserts every `event_routes` value resolves to a pipeline file whose declared `id:` matches.
17. **`scripts/validate.py` restored to running the full chain** — V8.2 had silently dropped four of V8.1's validators. All seven now run.

## Validator updates

18. `validate_v8_2_control_plane.py` and `validate_v8_control_plane.py` updated to allow `null` model when `model_unassigned_reason` is present (for Owen).
19. `validate_v8_control_plane.py` updated to accept `paperclip-org-import.v8.2` schema version.

## Validation

All seven validators pass:

```
$ python3 scripts/validate.py
PASS: Arthur model claims consistent across all non-deprecated surfaces.
PASS: V8.2 Arthur purge, contracts, producers, retry ladder, and route checks validated.
PASS: V8.1 Paperclip control-plane layer validated.
PASS: V7 namespaced pipeline validated.
PASS: Caveman full policy and Arthur escalation handoff validated.
PASS: Full Software House Arthur head and hiring authority validated.
PASS: all 9 event_routes resolve to existing pipeline files.
ALL VALIDATORS PASS
```

## Bug class addressed

V7 → V8 → V8.1 → V8.2 each fixed the specific phrases the previous audit called out. The new `validate_arthur_consistency.py` checks the **pattern** (Arthur mentioned near any non-canonical model keyword) rather than specific strings, so the next variant of the same bug cannot pass silently.
