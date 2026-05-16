<div align="center">

# 🏛 Pantheon

### **33 AI agents. One company. Zero humans in the loop.**

*Your software house ships PRs while you sleep.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OS](https://img.shields.io/badge/OS-Linux%20%7C%20macOS%20%7C%20WSL-brightgreen)](README_INSTALL.md)
[![Models](https://img.shields.io/badge/Models-Anthropic%20%7C%20OpenAI%20%7C%20Google%20%7C%20DeepSeek-blue)](#-the-pantheon)
[![Install](https://img.shields.io/badge/Install-One%20Click-orange)](#-quick-start)
[![Stars](https://img.shields.io/github/stars/5percentdrops/pantheon?style=social)](https://github.com/5percentdrops/pantheon/stargazers)

```
You write the PRD.   Pantheon ships the PR.
```

</div>

---

## ⚡ Install in 30 seconds

```bash
git clone https://github.com/5percentdrops/pantheon.git && cd pantheon && bash scripts/one_click_install.sh -y --setup-keys
```

That's it. 32 AI engineers wake up. Each has a name, a personality, a memory, and a job.

---

## 💥 Why this exists

**Problem:** You're a solo dev with the ambition of a 30-person studio.
You can't hire. You can't clone yourself. You can prompt an LLM — once, for one task, with no memory.

**Pantheon:** A persistent 33-agent software studio that runs locally, remembers everything, reviews its own code, and merges its own PRs. Each agent is a distinct identity with its own home, soul, memory, and skill library. They report up an org chart. They escalate when stuck. They learn from their mistakes.

It's not a wrapper. It's a **company**.

---

## 🎯 The 30-second pitch

| | Before Pantheon | With Pantheon |
|---|---|---|
| **Writing a feature** | You + ChatGPT, one tab, no memory | PRD → Arthur routes → Marcus designs → Jack codes → Clara reviews → Cody re-reviews → merge |
| **Code review** | "Looks fine to me" | Dual-pass Claude Opus 4.7 + GPT-5.5 Codex, with conditional escalation to specialists |
| **Memory** | Vanishes when tab closes | Per-agent `SOUL.md` + `MEMORY.md` + skill library, persistent forever |
| **Learning** | You re-prompt the same fix daily | Cody writes a skill the first time, applies it the next 1000 |
| **Scaling** | You hire engineers | You add API keys |

---

## 🏛 The Pantheon

33 named agents, each with a job, a model, and a will.

```
                            👤 YOU (Board / Final Approval)
                                         ↓
                            🎯 Arthur — Project Manager
                                         ↓
                         ┌───────────────┼───────────────┐
                         ↓               ↓               ↓
                  🏗 Architecture     🔨 Build      🧪 Quality
                  Marcus, Priya     Jack, Ben...   Nadia, Stone
                                         ↓
                                    📜 PR opened
                                         ↓
                              👀 Clara (Opus 4.7)
                                         ↓
                              👀 Cody (GPT-5.5 Codex)
                                         ↓
                         🔐 Safiya · 🏛 Priya · 🧪 Nadia
                                         ↓
                              🔥 Maxwell (Opus Max)  ← if Cody fails ×2
                                         ↓
                              ✅ Arthur merges
                                         ↓
                              📚 Winston archives
```

| Role | Agents |
|---|---|
| 🎯 **Head** | Arthur (PM, GPT-5 mini) |
| 🏗 **Architecture** | Marcus, Priya (Opus 4.7) |
| 🔨 **Senior build** | Marcus · Magnus (Gemini 3.1 Pro) · Maxwell (Opus 4.7 Max) |
| 👷 **Engineers** | Jack, Ben, Ivan, Theo, Leo, Ellie, Grant (DeepSeek V4 Pro) |
| 🎨 **Specialists** | Felix (Pine Script), Henrik, Oscar, Mira, Sonia, Viktor, Dominic, Nathan, Vera, Graham |
| 👀 **PR review (dual)** | Clara (Claude Opus 4.7) → Cody (GPT-5.5 Codex) |
| 🛡 **Quality & security** | Nadia (QA), Safiya (Security), Stone (perf), Adrian (release) |
| 📚 **Knowledge** | Winston (Claude 3.5 Haiku, wiki archive) |
| 🌐 **Domain** | Chloe, Dante (Kimi K2), Elena (Sonnet 4.6) |
| 🌒 **Dormant** | Owen (waiting on NotebookLM API) |

**Model spread:** Anthropic 15 · DeepSeek 7 · OpenAI 5 · Google 3 · Moonshot 2.
**Every agent runs on Hermes.** One harness, 33 identities, total isolation.

---

## 🧠 What makes this different

### 🪞 Each agent has a soul

```
~/.hermes-marcus/
  ├── SOUL.md       ← who they are
  ├── MEMORY.md     ← what they've learned (grows forever)
  ├── USER.md       ← who they report to (you)
  ├── skills/       ← skills they wrote themselves
  └── sessions/     ← FTS5-searchable session history
```

Fire up the same machine next year. Marcus remembers the architecture decision he pushed back on in March. Clara still knows the bug pattern she flagged in your auth flow. Cody still has the skill he wrote the first time he saw a race condition.

### ♻️ Self-improving loop

Agents write skills *to themselves* after solving a problem. The next agent to hit the same pattern reads it and skips the discovery phase. Your studio gets smarter every week, not slower.

### 🌙 Nightly Dreaming (V8.6)

At 03:00 UTC every agent runs a Dreaming pass in its own home: 7 days of sessions reviewed, duplicate skills `sha256`-dedup'd, `MEMORY.md` consolidated. `SOUL.md` / `USER.md` / `config.yaml` are immutable. No cross-agent reads. Compounding quality gains while you sleep.

### 🛑 Mid-pipeline QA gate (V8.6)

Marcus's SDD doesn't reach Jack's TDD block until Nadia (Senior QA, Opus 4.7 XHigh) signs it off against the PRD. Max 2 return cycles before Arthur escalates. Catches PRD-to-SDD drift at design time, not at PR review.

### 📐 Rubric-graded reviews (V8.7)

Clara grades implementations against a per-ticket `outcome.schema.json` rubric — `must_have` criteria, `must_not` anti-criteria, score floor 0.85 — with cited file:line evidence per criterion. Jack auto-iterates against the rubric before Cody ever sees the PR. End of "looks fine to me."

### ⚡ Fan-out engineer pool (V8.7)

When Marcus emits ≥2 tickets with no inter-dependency, Arthur dispatches across 4 parallel DeepSeek engineers (Jack/Ben/Ivan/Theo/Leo/Ellie/Grant) instead of serialising. Serial fallback on git-index contention. Opt-in per project after the smoke ramp.

### 💰 Per-host budget watcher (V8.7)

Arthur-owned cron at `*/30 * * * *` sums per-agent token-proxy bytes, emits WARN at 80% / CRIT at 95% of daily cap. CRIT lands in Arthur's `MEMORY.md` so he reads it on the next dispatch. Zero LLM calls, pure file IO.

### 📦 Rigid escalation contract (V8.8)

When Jack burns 21 attempts and hands to Marcus, the handoff is a strict `engineer_escalation_packet.v1` JSON — RTK-compressed trace, red test IDs, blocked-on enum, git SHA reference. Raw conversational text is rejected. Opus 4.7 stops paying input-token tax on transcript parsing.

### 🌐 Cross-agent learning (V8.8)

V8.6 dreaming kept lessons per-agent. V8.8 wires Winston to scrape every home at 04:00 UTC, dedup by sha256, and write a single `workspace/wiki/lessons_learned.md` that engineers pre-read before TDD. Jack stops relearning what Marcus already knew. **Live: 42 lessons extracted on first run.**

### 🔥 Maxwell override grading (V8.8)

Maxwell (Opus 4.7 Max) is the most expensive agent. His overrides used to auto-merge. Now Cody (GPT-5.5) re-grades against the **same** outcome rubric Clara used on Jack. Max 2 iterations → Magnus (architecture review) if the override still fails. No more silent acceptance of confident-wrong senior fixes.

### 🎛 Stack you control

```
Paperclip    →  company / control plane (1 instance)
hermes_local →  external Paperclip adapter (npm: hermes-paperclip-adapter)
HERMES_HOME  →  per-agent identity root
hermes       →  runtime invoked per task
LLMs         →  whatever you put your money on
```

No vendor lock. No hidden state. No SaaS. **Your machine, your models, your keys, your agents.**

---

## 🚀 Quick start

### 1. Prereqs (5 min, one time)

```bash
node --version          # ≥ 20
python3 --version       # ≥ 3.11
npm install -g paperclipai      # ≥ 2026.513.0
# Install hermes per https://github.com/NousResearch/hermes-agent
```

### 2. Pull Pantheon

```bash
git clone https://github.com/5percentdrops/pantheon.git
cd pantheon
```

### 3. Fire it up

```bash
bash scripts/one_click_install.sh -y --setup-keys
```

The installer will:

1. ✅ Validate (15+ checks)
2. ⚙️  Convert to `agentcompanies/v1` package
3. 🏠 Bootstrap **32 per-agent Hermes homes**
4. 🔌 Register `hermes_local` adapter
5. 🔑 Securely prompt for API keys (hidden input, `chmod 600`, zero network)
6. 🏛 Import the Pantheon into Paperclip

### 4. Ship something

```
Open Paperclip → Pantheon → Arthur
Send: "Build a CLI tool that counts unique words in a file."
Watch 6 agents collaborate. Get a merged PR.
```

---

## 🛡 Security posture

- 🔒 `setup_api_keys.sh` — `umask 077` · `chmod 600` · `read -s` (no echo) · atomic writes · zero network
- 🚫 No keys, `.env`, or PEM files in repo (`.gitignore` enforces)
- 🚷 `production trading keys forbidden in general agents` — policy-enforced
- 🧱 Per-agent isolation: `--per-agent` mode for env separation
- 🔐 Dual PR review + conditional security escalation to Safiya

---

## 📊 Verify the install

```bash
paperclipai adapters list | grep hermes_local         # ✅ adapter registered
paperclipai company list                              # ✅ Pantheon present
ls -d ~/.hermes-* | wc -l                             # ✅ 32 (Owen skipped)
python3 scripts/validate_hermes_local_package.py      # ✅ 32 routed
```

---

## 🌍 OS matrix

| OS | Status |
|---|---|
| 🐧 Linux | ✅ |
| 🍏 macOS | ✅ |
| 🪟 Windows (WSL2) | ✅ |
| 🪟 Windows native | ❌ — use WSL (full reason in [`README_INSTALL.md`](README_INSTALL.md)) |

---

## 🗺 Re-run flags

```bash
bash scripts/one_click_install.sh -y --validate-only        # validators only
bash scripts/one_click_install.sh -y --convert-only         # generate package
bash scripts/one_click_install.sh -y --no-bootstrap         # skip 32-home step
bash scripts/one_click_install.sh -y --skip-adapter-install # skip adapter register
bash scripts/one_click_install.sh -y --no-paperclip         # skip company import
bash scripts/one_click_install.sh -y --setup-keys           # add secure key prompt
bash scripts/one_click_install.sh -y --no-dreaming          # V8.6: skip nightly Dreaming cron
```

---

## ❓ FAQ

**Q: Is this AGI?**
No. It's a coordination layer over the LLMs you already pay for, with persistent identity per agent.

**Q: How much will it cost to run?**
Token usage scales with the work, not the agent count. An idle agent burns nothing. Heavy day ≈ a few dollars of Anthropic + OpenAI traffic.

**Q: Can I add my own agent?**
Yes. Drop a `.md` file in the company tree, give them a model, run the converter. They wake up next install.

**Q: Why "Pantheon"?**
33 named entities with distinct powers, organised under one head, reporting to a higher authority. Sound familiar?

**Q: Can the agents see my code?**
Only the code you give them. Each agent runs in its own `~/.hermes-<slug>/` sandbox.

**Q: What if an agent goes off the rails?**
Three layers stop it: per-agent budget caps, dual PR review (Clara + Cody), and human approval gates on merge / deploy / production trading rules.

---

## 📚 Deeper docs

- [`README_INSTALL.md`](README_INSTALL.md) — full install guide, OS matrix, key setup
- [`SMOKE_SCALE.md`](SMOKE_SCALE.md) — phased 3→33 agent ramp (don't fire all 33 on day one)
- [`PATCH_NOTES_V8_8.md`](PATCH_NOTES_V8_8.md) — escalation packet schema + cross-agent learning + Maxwell override grading
- [`PATCH_NOTES_V8_7.md`](PATCH_NOTES_V8_7.md) — outcome rubric + fan-out + budget watcher + CMA burst
- [`PATCH_NOTES_V8_6.md`](PATCH_NOTES_V8_6.md) — mid-pipeline QA + per-agent Dreaming
- [`PATCH_NOTES_V8_5.md`](PATCH_NOTES_V8_5.md) — Hermes-as-harness rollout
- [`ROLLBACK_TO_V8_4.md`](ROLLBACK_TO_V8_4.md) — one-command revert
- [`docs/PAPERCLIP_HERMES_CONTROL_PLANE_V8.md`](docs/PAPERCLIP_HERMES_CONTROL_PLANE_V8.md)
- [`docs/FULL_PANTHEON_ARTHUR_HEAD.md`](docs/FULL_PANTHEON_ARTHUR_HEAD.md)
- [`docs/UNIVERSAL_ORGANISATION_ESCALATION_PATTERN.md`](docs/UNIVERSAL_ORGANISATION_ESCALATION_PATTERN.md)
- [`docs/FINAL_PANTHEON_MODEL_MAP.md`](docs/FINAL_PANTHEON_MODEL_MAP.md)

---

## 🚧 Boundary

Pantheon **does not** install Paperclip, Hermes, OpenClaw, provider API keys, or production trading keys. It stages a company/org package. **Bring your own runtime, your own keys, your own ambition.**

---

## 📜 License

MIT — see [`LICENSE`](LICENSE).

---

<div align="center">

### 🌟 If Pantheon ships its first PR for you, [drop a star.](https://github.com/5percentdrops/pantheon/stargazers)

*Make AI work for you, not the other way around.*

</div>
