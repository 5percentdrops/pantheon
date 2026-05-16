# Contributing to Software House

## Adding or modifying an agent

Every agent is defined in **two places** in this repo:

1. **`agents/<desk>/<agent-id>.md`** — the human-readable spec, with YAML frontmatter and Markdown sections.
2. **`data/software-house-agents.json`** — the machine-readable bundle the onboarding prompt fetches and iterates over.

When you change an agent, update `(1)` and regenerate `(2)`.

### Step 1: Edit or add the Markdown file

Use `agents/SCHEMA.md` as the canonical reference for the file format.

Every agent file needs:

- YAML frontmatter with: `id`, `name`, `desk`, `runtime` (`hermes` | `openclaw`), `model`, `reports_to`, `supervises`, `consumes_from`, `produces_for`, `triggers`, `frequency`, `priority`, `tools`, `storage`
- Markdown sections: `## Personality`, `## Role`, `## Inputs`, `## Outputs`, `## Skills`, `## Rules of Engagement`, `## Failure Modes`, `## Prompt Stub`

Keep personalities distinct. The whole system depends on each agent having a different voice — uniform agents produce groupthink.

### Step 2: Regenerate the JSON bundle

Run the build script:

```bash
python3 scripts/build_bundle.py
```

This re-parses every `.md` file in `agents/` and writes `data/software-house-agents.json`. Check `git diff data/software-house-agents.json` before committing to confirm only the fields you intended to change are modified.

### Step 3: Update the manifest if the roster changed

If you added or removed an agent, update `manifest.yaml`:

- Add the agent to its desk's `agents:` list
- Add the agent to `agent_index:`
- Update the `runtime_summary` counts

### Step 4: Test the onboarding prompt

The cheapest way to test is to spin up a throwaway Paperclip house on your machine:

1. Run the onboarding prompt in Claude Code as normal
2. Use a test Supabase project (free tier)
3. Verify every new/changed agent appears in the org chart with correct instructions
4. Delete the test company from Paperclip after verifying

## Changing the desk structure

Desks are the top-level org units. Adding a new desk requires:

1. Create `agents/<new-desk>/` directory
2. Add agent files for the desk (at minimum, a senior advisor)
3. Update `DESK_ORDER` in `scripts/build_bundle.py`
4. Update `HEAD_PREFERENCES` in `scripts/build_bundle.py` (pick the senior advisor as the desk head)
5. Update `FLOW.md` to show how this desk fits into the pipeline
6. Update `manifest.yaml`

## Changing the Brain/Hands model assignments

Advisor roles default to Opus 4.7 (via Hermes). Executor roles split by domain:

- Code-heavy (Backend / Frontend / PineScript): Opus 4.6
- Mobile code: Sonnet 4.6
- Mobile UI design: Kimi K2.6
- DevOps mechanical: Haiku 4.5
- QA / Testing: Kimi K2.5
- Data pipelines: Sonnet 4.6
- Backtester: no LLM (pure Python via OpenClaw)

If you change an executor model, update the agent's `model:` field and re-run the build script.
