# Software House V8.5 — Install Guide

## Correct stack model (V8.5)

```text
Paperclip       company/control plane
hermes_local    external Paperclip adapter (hermes-paperclip-adapter)
HERMES_HOME     per-agent identity root  (~/.hermes-<slug>; 32 of them)
Hermes          runtime invoked per task, with HERMES_HOME injected
LLM models      provider/model passed through to Hermes
```

## OS compatibility

| OS | Status | Notes |
|---|---|---|
| Linux | Supported | Bash 4+, Python 3.11+ |
| macOS | Supported | Bash via Homebrew or system `/bin/bash`; default zsh OK (scripts use `#!/usr/bin/env bash`) |
| Windows (WSL2) | Supported | Install **paperclipai** and **hermes** inside the WSL distro, not Windows-side. Clone the repo to the WSL filesystem (`~/projects/...`), **not** `/mnt/c/...` — POSIX perms (`chmod 600`, `umask 077`) break on DrvFs |
| Windows native (cmd / PowerShell) | **Not supported** | All installer/bootstrap scripts are `#!/usr/bin/env bash` with `set -euo pipefail`. No `.ps1` / `.bat` wrappers ship in V8.5. Git Bash may partially work but `chmod 600` in `setup_api_keys.sh`, `~/` expansion, and `hermes doctor` env inheritance are unreliable. Use WSL2 |

Required on PATH (any OS): `bash`, `python3` (>=3.11), `node` (>=20), `npm`, `git`, `curl`, `paperclipai` (>=2026.513.0), `hermes`.

## Quickstart (V8.5 — Linux / macOS / WSL2)

### 1. Prereqs (one time)

```bash
# Runtimes
node --version   # >= 20
python3 --version # >= 3.11
git --version
curl --version

# Paperclip (control plane)
npm install -g paperclipai      # pins >= 2026.513.0
paperclipai --version
paperclipai run &               # starts API on :3100; run in tmux/systemd in prod

# Hermes (runtime)
# Install per https://github.com/NousResearch/hermes-agent (curl|bash quickstart)
hermes --version
hermes doctor
```

### 2. API keys (two options)

**Option A — Guided secure setup (recommended)**

Inside the extracted repo:

```bash
bash scripts/setup_api_keys.sh                 # interactive; input hidden; writes ~/.hermes/.env (chmod 600)
bash scripts/setup_api_keys.sh --per-agent     # write a separate .env per ~/.hermes-<slug>/ for isolation
bash scripts/setup_api_keys.sh --overwrite     # rotate existing keys
bash scripts/setup_api_keys.sh --dry-run       # show plan, no writes
```

The script:
- Hides keys as you type (no echo to terminal).
- Sets `umask 077` and writes `.env` with `chmod 600` (owner-only).
- Idempotent: re-runs preserve existing keys unless `--overwrite`.
- Never logs values; only key NAMES appear in summaries.
- No network calls; keys stay on this machine.

You can also run it as part of one-click install:

```bash
bash scripts/one_click_install.sh -y --setup-keys
```

**Option B — Manual (`~/.hermes/.env`)**

```bash
ANTHROPIC_API_KEY=...     # 15 agents (provider: auto)
OPENAI_API_KEY=...        # 5 agents  (provider: openai-codex)
OPENROUTER_API_KEY=...    # 10 agents (provider: openrouter — Gemini + DeepSeek)
# Optional, Kimi/Moonshot — covers 2 agents (provider: kimi-coding)
MOONSHOT_API_KEY=...
# Optional, GitHub-touching agents (15 of them)
GH_TOKEN=...
```

Verify Hermes sees each provider:

```bash
hermes doctor
hermes model    # interactive: pick claude-opus-4.7, gpt-5-mini, gemini-3.1-pro,
                #              deepseek-v4-pro, kimi-k2 — each should connect
```

### 3. Install Software House V8.5

```bash
unzip SoftwareHouse_V8_5_OneClickInstall_HermesHarness.zip
cd SoftwareHouse_V8_5_OneClickInstall_HermesHarness
bash scripts/one_click_install.sh -y
```

Internally:

1. Workspace mkdir.
2. Run all validators (14 of them).
3. Render legacy V8.x payload (back-compat).
4. Convert to `agentcompanies/v1` tree at `./software-house/` with `hermes_local` adapter for all 32 active agents + Owen-skip.
4b. Post-convert validators (package + hermes_local schema).
5. Bootstrap 32 `~/.hermes-<slug>/` homes (config.yaml + SOUL.md + MEMORY.md + USER.md + skills/seed.md).
6. Register `hermes_local` adapter plugin in `~/.paperclip/adapter-plugins.json`.
7. `paperclipai company import` (dry-run preview → real import on confirmation).

### 4. Verify

```bash
paperclipai adapters list | grep hermes_local         # hermes_local present
paperclipai company list                              # "Software House" present
ls -d ~/.hermes-* | wc -l                             # 32 (Owen skipped)
python3 scripts/validate_hermes_local_package.py      # OK: 32 routed, 1 skipped
```

### 5. First real task (smoke)

In the Paperclip UI:
1. Open the `Software House` company.
2. Locate `arthur` (Project Manager, top of org chart).
3. Send a small PRD: `"Build a CLI tool that counts unique words in a file."`
4. Watch Arthur route. Expect:
   - Arthur spawns with `HERMES_HOME=~/.hermes-arthur hermes …`
   - Arthur produces an SDD seed, hands to Marcus (senior backend).
   - Marcus opens a ticket, hands to Jack (junior backend).
   - Jack writes TDD red tests, then code; Clara/Cody review.
   - Maxwell escalates if Cody fails twice.
   - Winston archives the final artifact.

Each downstream agent runs in its own home (`~/.hermes-marcus`, `~/.hermes-jack`, etc.).

### 6. Re-run flags (idempotent)

```bash
bash scripts/one_click_install.sh -y --validate-only          # validators only
bash scripts/one_click_install.sh -y --convert-only           # generate package, no install
bash scripts/one_click_install.sh -y --no-bootstrap           # skip 32-home step
bash scripts/one_click_install.sh -y --skip-adapter-install   # skip adapter register
bash scripts/one_click_install.sh -y --no-paperclip           # skip company import
bash scripts/one_click_install.sh -y --setup-keys             # add secure API key prompt step
```

### 7. Rollback

See `ROLLBACK_TO_V8_4.md` for the full revert path.

---

## Legacy install path

From repo root:

```bash
bash scripts/one_click_install.sh
```

This will:

1. Create/validate workspace folders.
2. Validate the existing V7 pipeline.
3. Validate V8 Paperclip control-plane files.
4. Validate Hermes-only harness policy.
5. Validate canonical agent IDs.
6. Stage a Paperclip company import payload.

Generated outputs:

```text
.stage/paperclip_company.import.json
SoftwareHouse/paperclip/paperclip_company.import.json
```

## Compatibility installer

The old path still works:

```bash
bash scripts/install.sh
```

It now wraps the V8 installer and stages Paperclip/Hermes files. It intentionally does **not** install OpenClaw seeds as active harnesses.

## Boundary

This repo does not install Paperclip, Hermes, OpenClaw, provider API keys, or production trading keys.

It stages a company/org package for Paperclip and Hermes-based workers.


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
