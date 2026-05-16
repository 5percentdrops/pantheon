# SoftwareHouse Standalone Plug-and-Play Package

This package applies the same final CoreSeed standard used for FeedDeck, StoryVision, and Theseus House.

## Includes

- Organisation name
- Agents
- Roles
- Descriptions
- Personalities
- LLM/module assignments
- Harness assignments
- Paperclip organisation import
- Hermes seed skills
- OpenClaw seed skills
- Routes / handoff maps
- Escalation schemas
- Validation script
- Install script
- Original source repo for audit

## Main contact

Arthur — Project Manager

## Install

```bash
python3 scripts/validate.py
bash scripts/install.sh
```

## Key changes from original

- Added Priya — System Architect.
- Added Safiya — Security Reviewer.
- Added seed skills for every Hermes/OpenClaw agent.
- Added OpenClaw escalation rules.
- Kept the Brain/Hands operating model.


## Codex PR Reviewer

Software House now includes **Cody — Codex PR Reviewer**.

Codex review is a required PR gate after a pull request is opened/submitted and before merge readiness.

Flow:
implementation → PR opened/submitted → Codex PR review → revise/block/approve → QA/security/architecture as needed → Project Manager merge readiness.


## Hermes Codex PR Reviewer correction

Cody now uses **Hermes as the harness** and **Codex as the underlying code-review engine**.

This means Cody can:
- review PR diffs with Codex,
- recognise new code patterns,
- learn repeated fixes,
- detect recurring bug classes,
- create Hermes learning candidates,
- improve future reviews over time.

Preferred Codex model when configurable: **GPT-5.2-Codex**.
Fallback: latest Codex default available in the installed Codex environment.


## Dual PR Review Update

Software House now uses two separate Hermes-harnessed PR reviewers:

1. **Clara — Claude PR Review Lead**
   - Harness: Hermes
   - Underlying engine: Claude Code Review / Opus 4.7
   - First-line deep PR review

2. **Cody — Hermes Codex PR Reviewer**
   - Harness: Hermes
   - Underlying engine: latest Codex coding/review model
   - Second-line PR review and repeated-pattern learning

Specialist escalation is conditional:
- Safiya for security
- Priya for architecture
- Nadia for QA/tests
- Arthur for requirements and merge readiness

## V8 Paperclip + Hermes Control Plane Update

This repo now treats the stack correctly:

```text
Paperclip = company/control plane
Arthur = Project Manager / Head employee inside Paperclip
Hermes = harness/runtime over selected LLM models
LLM models = GPT-5 mini, GPT-5.5, Opus 4.7 XHigh/Max, Gemini Pro 3.1, DeepSeek V4 Pro, etc.
```

The canonical installer is:

```bash
bash scripts/one_click_install.sh
```

The installer validates the V7 pipeline, validates the V8 Paperclip control-plane layer, and stages:

```text
.stage/paperclip_company.import.json
SoftwareHouse/paperclip/paperclip_company.import.json
```

Core hard gates:

- Context pack before non-trivial work.
- Architecture before tickets.
- Tests before code.
- Green before next task.
- Green + reviewed before merge.
- Human approval for governance, merge, deployment, production trading rules, and API-key permission changes.
- No production trading keys inside general Paperclip/Hermes workers.
- Execution cannot invent trades.
- Automated sizing must use fractional Kelly only.


## V8.1 integrity patch

V8.1 fixes the V8 audit issues:

- `model` is now the canonical model field.
- Arthur is collapsed to `openai/gpt-5-mini` under Hermes.
- `llm_module` is display-only and derived from `model`.
- `SoftwareHouse/contracts/` is the canonical schema directory.
- Routes and pipelines are validated against contracts.
- Pipelines are dispatchable through `event_routes`.
- Context-pack-first is validated structurally.
- OpenClaw active harness/seed material is disabled and moved to deprecated history.
- Budget caps are sanity-checked.


## V8.2 hardening note

V8.2 removes the remaining stale Arthur model declarations and makes `model` canonical.

```text
Arthur model: openai/gpt-5-mini
Arthur display: GPT-5 mini under Hermes
Paperclip: company/control plane
Hermes: harness/runtime over selected LLMs
```

V8.2 also adds:

- canonical engineering escalation ladder
- artifact producers for heartbeat/transcript/budget events
- model route override lifecycle
- stronger merge review schema with reviewer identity
- validator checks for stale Arthur model references

## V8.5 runtime model — Hermes-as-harness

**Every agent runs on Hermes.** V8.5 replaces V8.4's mixed `claude_local` / `codex_local` / `gemini_local` adapter split with a uniform `hermes_local` adapter (from npm `hermes-paperclip-adapter`, loaded via Paperclip's external adapter plugin loader at `~/.paperclip/adapter-plugins.json`).

```text
Paperclip          company/control plane (1 instance)
hermes_local       external adapter (1 plugin, loaded into Paperclip)
HERMES_HOME        per-agent identity root (~/.hermes-<slug>, 32 of them)
hermes             runtime invoked per task with HERMES_HOME injected
LLM models         provider/model passed through to Hermes (Anthropic, OpenAI, Google, DeepSeek, Kimi)
```

Each agent gets `~/.hermes-<slug>/`:

- `config.yaml` — model + provider + toolsets seeded by the bootstrap script
- `SOUL.md` — agent's role + personality (extracted from AGENTS.md body)
- `MEMORY.md` — persistent, grows across heartbeats
- `USER.md` — main contact (Arthur)
- `skills/` — seed skill + any skills the agent writes itself post-task

Run:

```bash
bash scripts/one_click_install.sh -y
```

Internally: validate → convert → **bootstrap 32 Hermes homes** → **install `hermes_local` adapter plugin** → `paperclipai company import`.

Owen (NotebookLM) is intentionally skipped at import (no API to shell to). The org-chart record remains; the adapter block is omitted. Re-enable when NotebookLM exposes an API or the workflow moves to Gemini 3.1 Pro.

Full patch notes: `PATCH_NOTES_V8_5.md`. Rollback to V8.4: `ROLLBACK_TO_V8_4.md`.
