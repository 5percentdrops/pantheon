# V8.5 Patch Notes — Hermes-as-harness one-click install

V8.4 shipped a 33-agent Paperclip company that ran each agent via the agent's native CLI (`claude_local` for Anthropic, `codex_local` for OpenAI/DeepSeek/Kimi, `gemini_local` for Google). V8.4 patch notes called Hermes-per-agent "Phase 2 — requires custom adapter."

That claim was stale. The adapter already exists.

V8.5 wires every agent to `hermes_local` — Paperclip's external adapter type provided by [hermes-paperclip-adapter](https://www.npmjs.com/package/hermes-paperclip-adapter) (mirror of `NousResearch/hermes-paperclip-adapter`). Each agent gets its own `HERMES_HOME`, its own `SOUL.md`, its own `MEMORY.md`, its own session and skill library. The self-improving skill loop and persistent memory are active per-agent.

## What changed

### 1. Uniform adapter: `hermes_local`

`scripts/convert_to_agentcompanies_v1.py` `ADAPTER_MAP` (L46–52) and `map_adapter()` (L79–93) now emit `adapter.type: hermes_local` for every agent. Provider field per model family:

| Model family | `model` | `provider` |
|---|---|---|
| `anthropic/claude-*` | as-is | `auto` |
| `openai/gpt-*` | as-is | `openai-codex` |
| `google/gemini-*` | as-is | `openrouter` |
| `deepseek/*` | as-is | `openrouter` |
| `moonshotai/kimi-*` | as-is | `kimi-coding` |

Owen (`null` model) is skipped at import (no adapter block emitted). Owen's agent record + AGENTS.md remain so the org chart is intact; re-enable when NotebookLM exposes an API or the workflow moves to Gemini 3.1 Pro.

### 2. Per-agent `HERMES_HOME`

The converter emits this block in each agent's `.paperclip.yaml`:

```yaml
adapter:
  type: hermes_local
  config:
    model: anthropic/claude-opus-4.7
    provider: auto
    toolsets: terminal,file,web,browser,code_execution,mcp
    timeoutSec: 300
    graceSec: 10
    env:
      HERMES_HOME: ~/.hermes-marcus
```

Hermes is one identity per `HERMES_HOME`. 32 distinct homes (Owen skipped) give 32 distinct Hermes identities, each with their own SOUL/MEMORY/skills.

### 3. New: `scripts/bootstrap_hermes_homes.sh`

Replaces V8.4 `install_to_hermes.sh` single-home logic. For each of the 32 active agents:

1. `mkdir -p ~/.hermes-<slug>`
2. Write `~/.hermes-<slug>/config.yaml` (model+provider+toolsets from the agent's adapter block)
3. Copy `Pantheon/skills/hermes_seed/skill_<canonical_id>_seed.md` → `~/.hermes-<slug>/skills/seed.md`
4. Extract agent's AGENTS.md body → `~/.hermes-<slug>/SOUL.md`
5. Write `~/.hermes-<slug>/MEMORY.md` (seeded with role + `reportsTo` + workflow position)
6. Write `~/.hermes-<slug>/USER.md` (from `manifest.main_contact`)
7. `HERMES_HOME=~/.hermes-<slug> hermes doctor` for verification

`install_to_hermes.sh` is preserved as a deprecated shim that calls `bootstrap_hermes_homes.sh` (back-compat).

### 4. New: `scripts/install_hermes_adapter_plugin.sh`

Idempotent. Writes (or merges into) `~/.paperclip/adapter-plugins.json`:

```json
{
  "plugins": [
    { "type": "hermes_local", "package": "hermes-paperclip-adapter" }
  ]
}
```

Pre-flight: `paperclipai --version` ≥ `2026.513.0`, `hermes --version` reachable. Verifies via `paperclipai adapters list | grep hermes_local` post-install. Fallback to `file:` path if user clones the adapter for local dev.

### 5. New: `scripts/validate_hermes_local_package.py`

Asserts on the converter output (`pantheon/agents/<slug>/.paperclip.yaml`):

- `adapter.type == "hermes_local"`
- `adapter.config.model` non-empty
- `adapter.config.provider` non-empty
- `adapter.config.env.HERMES_HOME == "~/.hermes-<slug>"`
- Every canonical agent ID in `manifest.canonical_agent_ids` has a corresponding agent directory
- Owen agent dir exists but has no adapter block (allowed)

Added to the `validate.py` orchestrator chain.

### 6. Updated: `scripts/one_click_install.sh`

New step order:

1. Workspace mkdir
2. Run all validators (V8.4) + `validate_hermes_local_package.py`
3. Legacy render (back-compat)
4. Converter → `pantheon/`
5. **NEW: `bootstrap_hermes_homes.sh`** (creates 32 `~/.hermes-<slug>/`)
6. **NEW: `install_hermes_adapter_plugin.sh`** (registers `hermes_local` in Paperclip)
7. `install_to_paperclip.sh` → `paperclipai company import`

New flags:

```
--no-bootstrap          # skip step 5 (re-runs)
--skip-adapter-install  # skip step 6 (adapter already registered)
```

### 7. Updated: `scripts/install_to_paperclip.sh`

Pre-flight check adds `hermes --version` after `paperclipai --version`. Fails fast if Hermes missing on host.

### 7b. New: `scripts/setup_api_keys.sh` (opt-in, secure)

Interactive guided setup for provider API keys, opt-in only via `--setup-keys` flag on `one_click_install.sh` (or run directly). Designed so the only manual work outside the installer is installing the `paperclipai` and `hermes` binaries themselves.

Security model:

- `umask 077` before any write; files chmod `600` (owner read/write only).
- `read -s` for all key input; values never echo to terminal.
- Never logs key values; only key NAMES appear in summaries.
- Idempotent: re-runs preserve existing keys unless `--overwrite`.
- Atomic writes: temp file → chmod → rename, so partial failures don't leave readable junk.
- No network calls; keys never leave the host.
- Whitespace-bearing values rejected at capture time.

Modes:

```
bash scripts/setup_api_keys.sh                 # shared ~/.hermes/.env (Hermes inherits in every per-agent home)
bash scripts/setup_api_keys.sh --per-agent     # one .env per ~/.hermes-<slug>/ (isolation)
bash scripts/setup_api_keys.sh --overwrite     # rotate
bash scripts/setup_api_keys.sh --dry-run       # preview, no writes
```

Providers prompted (skip with Enter):

| Variable | Agents covered | Where to get |
|---|---|---|
| `ANTHROPIC_API_KEY` | 15 (Marcus, Maxwell, Clara, Winston, ...) | console.anthropic.com |
| `OPENAI_API_KEY` | 5 (Arthur, Cody, Adrian, Safiya, Stone) | platform.openai.com |
| `OPENROUTER_API_KEY` | 10 (Gemini + DeepSeek family) | openrouter.ai |
| `MOONSHOT_API_KEY` | 2 (Chloe, Dante; optional) | platform.moonshot.ai |
| `GH_TOKEN` | 15 GitHub-touching agents (optional) | github.com/settings/tokens |

Wired into `one_click_install.sh` via `--setup-keys`. Default behavior unchanged (does NOT prompt unless flag passed).

### 8. `manifest.json`

- `version` → `8.5`
- `schema_version` → `pantheon.v8.5`
- New top-level block `hermes_local_adapter` (pinned package, package version `^0.3.0` — official NousResearch package, min Paperclip `2026.513.0`, per-agent home template, registration path)
- New top-level block `v8_5_patch` (audit summary)

## Bug class addressed

| Class | V8.4 behavior | V8.5 fix |
|---|---|---|
| Agent has no persistent personality | Personality lived in Paperclip DB only; lost on company export/reimport | SOUL.md per agent, file-based, portable |
| No per-agent memory | Paperclip task history only — fresh context per heartbeat | MEMORY.md + USER.md per agent; Hermes `--resume` survives heartbeat |
| Self-improvement loop absent | Agent couldn't write new skills between tasks | Hermes per-agent skill library; agent autonomously writes `~/.hermes-<slug>/skills/<new>.md` post-task |
| No per-agent session search | Hermes FTS5 unused | Per-agent FTS5 search across own session history |
| Three adapter conventions | `claude_local`/`codex_local`/`gemini_local` split — three debug paths | Uniform `hermes_local` — one debug path, one log format, one CLI surface |

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Adapter npm name drift | Pinned **official** `hermes-paperclip-adapter@^0.3.0` (maintainer: teknium / Nous Research; repo: github.com/NousResearch/hermes-paperclip-adapter; license: MIT). A personal fork `@henkey/hermes-paperclip-adapter@0.4.3` exists at a higher version — do NOT substitute without audit. |
| Paperclip schema drift | Pinned `paperclipai>=2026.513.0` (latest stable at release) |
| `HERMES_HOME` not honored by adapter | Phase 2 smoke test (one agent, verify `$HERMES_HOME` populated post-task) required on target before scaling to 32 |
| Resource pressure (32 concurrent Hermes processes) | Paperclip queues on demand — only active agents have hot processes. Recommend Mac Mini M2 16GB+ for >8 concurrent. Tune `timeoutSec`/`graceSec` per agent. |
| `hermes setup` interactive | Bootstrap drops a pre-built `config.yaml` directly; skips the wizard. `hermes doctor` validates each home post-write. |

## Validation

Run after `one_click_install.sh -y` on the target host:

```bash
paperclipai adapters list                       # contains hermes_local
paperclipai company list                        # contains Pantheon w/ 33 agents
ls ~/.hermes-*                                  # 32 dirs (Owen skipped)
python3 scripts/validate_hermes_local_package.py
```

End-to-end: issue a PRD to Arthur. Verify Paperclip spawns `HERMES_HOME=~/.hermes-arthur hermes …` and the PRD→SDD→Ticket→TDD→PR pipeline completes with each downstream agent running in its own home.

## Rollback

`ROLLBACK_TO_V8_4.md` ships in this release. Single command reverts to V8.4 native adapters.
