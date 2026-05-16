# V8.4 Patch Notes — Real Paperclip one-click install

This is the patch that turns the V8.3 specification repo into an actual one-click install. V8.3 staged a JSON payload against an invented schema (`paperclip-org-import.v8.2`). Paperclip's real importer does not understand that schema. V8.4 converts the payload to the format Paperclip actually accepts: an `agentcompanies/v1` directory tree.

## What changed

### 1. New converter: `scripts/convert_to_agentcompanies_v1.py`

Reads `Pantheon/paperclip/organization.import.json` and the Hermes seed skills. Emits a `pantheon/` directory in the format Paperclip's `paperclipai company import` command expects:

```
pantheon/
  COMPANY.md          # YAML frontmatter: schema=agentcompanies/v1, name, slug, goals, license
  README.md           # human-readable overview, org chart, getting-started
  LICENSE             # MIT
  .paperclip.yaml     # Paperclip vendor extension: adapter mappings + governance + budget
  agents/<slug>/AGENTS.md     # one per agent (33 total) with reportsTo, skills, instruction body
  skills/<slug>/SKILL.md      # one per agent's seed skill (33 total)
```

Each agent's instruction body has a role description, a workflow-position block (where work comes from, what you produce, who you hand off to, hard rules), and the standard execution contract.

Stale "OPS 4.7 High under Hermes" / "DeepSeek V4 Pro under Hermes" strings in seed skills are canonicalized to the agent's real model identifier during conversion (e.g. `` `deepseek/deepseek-v4-pro` under Hermes ``).

### 2. New `.paperclip.yaml` (Paperclip vendor extension)

Per-agent adapter mappings. Each agent's V8.3 `model` field maps to a real Paperclip adapter:

| Model family | Adapter | Notes |
|---|---|---|
| `anthropic/claude-opus-4.7` | `claude_local` | with `effort: xhigh` or `max` where set |
| `anthropic/claude-3.5-haiku` | `claude_local` | |
| `openai/gpt-5-mini`, `openai/gpt-5.5` | `codex_local` | |
| `google/gemini-3.1-pro` | `gemini_local` | |
| `deepseek/deepseek-v4-pro` | `codex_local` | via OpenRouter (no native adapter) |
| `moonshotai/kimi-k2-*` | `codex_local` | via OpenRouter |

Hermes is **not** a first-class Paperclip adapter type. Paperclip's valid adapters are `claude_local`, `codex_local`, `opencode_local`, `pi_local`, `cursor`, `gemini_local`, `openclaw_gateway`. Hermes-as-runtime requires a custom Paperclip adapter (Phase 2 work).

Owen's `null` model is preserved with a comment block explaining that NotebookLM is a product, not an API.

GitHub-touching agents (jack, marcus, leo, sonia, ellie, dominic, ben, felix, grant, nathan, theo, viktor, cody, clara, maxwell) get a `GH_TOKEN` env input declared as `kind: secret, requirement: optional`.

Governance and budget policies are inlined under `governance:` and `budget:` blocks so Paperclip picks them up at import.

### 3. New installer: `scripts/install_to_paperclip.sh`

Real Paperclip import. Resolves the Paperclip CLI (`paperclipai`, `pnpm paperclipai`, or `npx paperclipai`). Checks the API at `http://localhost:3100` is reachable. Runs the converter. Runs `paperclipai company import --dry-run` for the preview. On confirmation, applies the real import.

### 4. New installer: `scripts/install_to_hermes.sh`

Wires the seed skills into a single Hermes installation as external read-only skills via `~/.hermes/config.yaml -> skills.external_dirs`. Copies skills to `~/.agents/skills/pantheon/` and prints the YAML block to paste.

This is explicitly **not** a multi-agent Hermes install. Hermes runs one identity per `HERMES_HOME`. For multi-agent Hermes you'd run 33 separate Hermes installations with different `HERMES_HOME` values, or build a custom Paperclip adapter. The installer notes this.

### 5. Updated `scripts/one_click_install.sh`

Full V8.4 flow:

1. Create workspace directories.
2. Run all 8 validators.
3. Render the legacy V8.x JSON (backward compat).
4. Run the agentcompanies/v1 converter.
5. Interactive: install to Paperclip? Wire skills into Hermes?

Modes:

```
bash scripts/one_click_install.sh                  # interactive
bash scripts/one_click_install.sh --validate-only  # validation only
bash scripts/one_click_install.sh --convert-only   # produce package, no install
bash scripts/one_click_install.sh --no-paperclip   # skip Paperclip
bash scripts/one_click_install.sh --no-hermes      # skip Hermes
bash scripts/one_click_install.sh -y               # non-interactive, apply everything
```

### 6. New validator: `scripts/validate_agentcompanies_v1_package.py`

Validates the generated `pantheon/` package:

1. Required files present (COMPANY.md, README.md, LICENSE, .paperclip.yaml).
2. COMPANY.md frontmatter has `schema: agentcompanies/v1` and `slug: pantheon`.
3. Every agent directory has an AGENTS.md with frontmatter (name, slug, title, description, reportsTo, skills).
4. Exactly one root (`reportsTo: null`) — must be Arthur.
5. All `reportsTo` slugs resolve to actual agent directories.
6. Every skill referenced in any AGENTS.md resolves to a real SKILL.md.
7. `.paperclip.yaml` uses only valid Paperclip adapter types.
8. No stale Arthur model strings in any generated file.

Wired into `scripts/validate.py`. Skips cleanly if the package hasn't been generated yet.

## What V8.4 does NOT do

Honest accounting:

- **Does not install Paperclip itself.** You need `pnpm install -g paperclipai` or a Paperclip clone running locally before the installer can import into it. The installer detects this and tells you.
- **Does not install Hermes itself.** Same — install Hermes first via the Nous Research one-liner.
- **Does not configure provider API keys.** Each adapter (`claude_local`, `codex_local`, `gemini_local`) expects its CLI to have its own API key. The Paperclip UI is where you wire those at import time.
- **Does not solve multi-agent Hermes identity.** Hermes has one SOUL/memory per HERMES_HOME. The 33 agents run under Paperclip's adapters, not as 33 Hermes processes. Hermes is a skill library here, not a runtime fleet.
- **Does not make Owen run.** Owen's `model` is `null` because NotebookLM is a product, not an API. You assign him a model in the Paperclip UI (Gemini 3.1 Pro is the candidate) or leave him paused.

## Verification

From a fresh extraction:

```
$ bash scripts/one_click_install.sh --convert-only
==> Step 1/5: Create workspace directories
==> Step 2/5: Run validators                            (8/8 PASS)
==> Step 3/5: Render legacy V8.x paperclip_company.import.json
==> Step 4/5: Convert to agentcompanies/v1 directory tree
  wrote COMPANY.md
  wrote README.md
  wrote LICENSE
  wrote 33 AGENTS.md files
  wrote 33 SKILL.md files
  wrote .paperclip.yaml
Convert-only mode. Package staged at: ./pantheon
```

The `pantheon/` directory is what you point `paperclipai company import --from ./pantheon` at.

## Sources

- Paperclip — https://github.com/paperclipai/paperclip
- Agent Companies specification — https://agentcompanies.io/specification
- company-creator skill (used to derive `.paperclip.yaml` structure and adapter rules) — https://skillsmp.com/skills/paperclipai-paperclip-agents-skills-company-creator-skill-md
- Hermes Agent — https://hermes-agent.nousresearch.com/docs/
- Hermes skills external_dirs config — https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/

## Bug class addressed

V7 -> V8 -> V8.1 -> V8.2 -> V8.3 fixed string-level Arthur model contradictions. V8.4 addresses a different bug class: the entire payload schema (`paperclip-org-import.v8.2`) was invented and would not have imported into the real Paperclip. The conversion + validation pipeline now produces a format the real tool accepts and verifies it on every run.
