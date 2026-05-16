# Software House

> AI-native software studio. 33 agents. One company. Runs on **Paperclip** (control plane) + **Hermes** (per-agent runtime).

```
Paperclip     →   company / control plane (1 instance)
hermes_local  →   external Paperclip adapter (npm: hermes-paperclip-adapter)
HERMES_HOME   →   per-agent identity root  (~/.hermes-<slug>, 32 active homes)
hermes        →   runtime invoked per task with HERMES_HOME injected
LLM models    →   Anthropic, OpenAI, Google, DeepSeek, Moonshot — passed through
```

Every agent has its own `SOUL.md`, `MEMORY.md`, `USER.md`, persistent session, and self-improving skill library. Identity survives heartbeats, machine moves, and company re-imports.

---

## Quick start

```bash
git clone https://github.com/5percentdrops/software-house-v8.5.git
cd software-house-v8.5
bash scripts/one_click_install.sh -y --setup-keys
```

That's it. Installer does: validate → convert → bootstrap 32 Hermes homes → register `hermes_local` adapter → `paperclipai company import`.

**Prereqs:** `bash`, `python3 ≥ 3.11`, `node ≥ 20`, `npm`, `git`, `curl`, [paperclipai](https://www.npmjs.com/package/paperclipai) `≥ 2026.513.0`, [hermes](https://github.com/NousResearch/hermes-agent).

**OS:** Linux ✅ · macOS ✅ · WSL2 ✅ · Windows native ❌ (use WSL — see [`README_INSTALL.md`](README_INSTALL.md))

---

## The company

33 agents organised under **Arthur** (Project Manager / Head). Domain leads, junior/senior engineers, dual PR review, escalation ladders, governance gates.

| Layer | Agents |
|---|---|
| **Head** | Arthur (PM, GPT-5 mini) |
| **Architecture** | Marcus (Opus 4.7), Priya (Opus 4.7) |
| **Build (senior)** | Marcus, Magnus (Gemini 3.1 Pro), Maxwell (Opus 4.7 Max) |
| **Build (engineers)** | Jack, Ben, Ivan, Theo, Leo, Ellie, Grant (DeepSeek V4 Pro) |
| **Specialists** | Felix (Pine Script), Henrik, Oscar, Mira, Sonia, Viktor, Dominic, Nathan, Vera, Graham |
| **PR review (dual)** | Clara (Claude Opus 4.7) → Cody (GPT-5.5 Codex) |
| **Quality & security** | Nadia (QA), Safiya (Security), Stone (perf), Adrian (release) |
| **Knowledge** | Winston (Claude 3.5 Haiku, wiki archive) |
| **Domain** | Chloe, Dante (Kimi K2), Elena (Sonnet 4.6) |
| **Skipped (no API)** | Owen (NotebookLM — re-enable when API ships) |

Model spread: Anthropic 15 · DeepSeek 7 · OpenAI 5 · Google 3 · Moonshot 2.

---

## What ships

```
scripts/                  38 files — one_click_install, validators, converters,
                          bootstrap, adapter installer, secure key setup
SoftwareHouse/            270 files — agents, routes, contracts, pipelines,
                          paperclip company import, skills, schemas, templates
docs/                     architecture, escalation patterns, model map
manifest.json             canonical org spec (33 agents, v8.5)
PATCH_NOTES_V8_*.md       version history (V8 → V8.5)
ROLLBACK_TO_V8_4.md       revert path
README_INSTALL.md         full install guide + OS matrix
```

---

## Pipeline

```
USER PRD
   ↓
Arthur (approval gate)
   ↓
Marcus  ─→  SDD  →  Feature Tickets  →  Task-level TDD
   ↓
Jack (sequential execution; green-before-next)
   ↓
PR opened
   ↓
Clara (Claude Opus first-line review)
   ↓
Cody (Codex second-line + pattern learning)
   ↓
[conditional] Safiya (security) · Priya (arch) · Nadia (QA)
   ↓
[escalation] Maxwell (Opus Max) if Cody fails ×2
   ↓
Arthur (merge readiness)
   ↓
Winston (archive to wiki)
```

Hard gates: context-pack before non-trivial work · architecture before tickets · tests before code · green before next task · green + reviewed before merge · human approval for governance, merge, deploy, prod trading rules, API-key permission changes.

---

## Security

- `setup_api_keys.sh`: `umask 077`, files `chmod 600`, `read -s` (no echo), atomic temp→rename, idempotent, zero network calls
- No keys, no `.env`, no PEM in repo — `.gitignore` blocks them
- `production trading keys forbidden in general agents` enforced at policy layer
- Per-agent isolation: each `~/.hermes-<slug>/` is independent; `--per-agent` mode for env separation

---

## Verify install

```bash
paperclipai adapters list | grep hermes_local         # adapter registered
paperclipai company list                              # Software House present
ls -d ~/.hermes-* | wc -l                             # 32 (Owen skipped)
python3 scripts/validate_hermes_local_package.py      # OK: 32 routed
```

Then smoke-test in the Paperclip UI: send Arthur the PRD `"Build a CLI tool that counts unique words in a file."` and watch the routing.

---

## Re-run flags

```bash
bash scripts/one_click_install.sh -y --validate-only        # validators only
bash scripts/one_click_install.sh -y --convert-only         # generate package
bash scripts/one_click_install.sh -y --no-bootstrap         # skip 32-home step
bash scripts/one_click_install.sh -y --skip-adapter-install # skip adapter register
bash scripts/one_click_install.sh -y --no-paperclip         # skip company import
bash scripts/one_click_install.sh -y --setup-keys           # add secure key prompt
```

---

## Docs

- [`README_INSTALL.md`](README_INSTALL.md) — full install guide, OS matrix, key setup
- [`PATCH_NOTES_V8_5.md`](PATCH_NOTES_V8_5.md) — Hermes-as-harness rollout
- [`ROLLBACK_TO_V8_4.md`](ROLLBACK_TO_V8_4.md) — one-command revert
- [`docs/PAPERCLIP_HERMES_CONTROL_PLANE_V8.md`](docs/PAPERCLIP_HERMES_CONTROL_PLANE_V8.md)
- [`docs/FULL_SOFTWARE_HOUSE_ARTHUR_HEAD.md`](docs/FULL_SOFTWARE_HOUSE_ARTHUR_HEAD.md)
- [`docs/UNIVERSAL_ORGANISATION_ESCALATION_PATTERN.md`](docs/UNIVERSAL_ORGANISATION_ESCALATION_PATTERN.md)
- [`docs/FINAL_SOFTWARE_HOUSE_MODEL_MAP.md`](docs/FINAL_SOFTWARE_HOUSE_MODEL_MAP.md)

---

## Boundary

This repo **does not** install Paperclip, Hermes, OpenClaw, provider API keys, or production trading keys. It stages a company/org package for Paperclip + Hermes-based workers. Bring your own runtime, bring your own keys, opt-in via `setup_api_keys.sh`.

---

## License

See repo settings. Internal use — verify before redistribution.
