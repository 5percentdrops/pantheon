# Software House

One-shot prompt to build a 21-agent AI-native software development house with Paperclip + Hermes + OpenClaw + Supabase. You provide the PRD, SDD, and JSX front-end draft. The house builds the product.

---

## What This Is

A single prompt you paste into Claude Code. It interviews you, installs Paperclip, provisions a Supabase schema, fetches a 21-agent bundle, hires the house with pre-loaded personalities and mandates, and opens the Paperclip dashboard — all in one session.

You end the session talking to the Project Manager (Hermes). The PM delegates to Senior Advisors. Senior Advisors write plans and hand them to their Executors. You never assign tasks downward of the PM.

---

## The Operating Model

**Brain / Hands pattern**, applied universally:

| Tier | Role | Model | What it does |
|---|---|---|---|
| **Advisor (Brain)** | Senior [Role] | Opus 4.7 via Hermes | Writes the plan. Reviews. Unblocks. Scarce resource. |
| **Executor (Hands)** | [Role] | Opus 4.6 / Sonnet 4.6 / Kimi / Haiku via Hermes | Follows the plan. High token volume on cheaper models. |

**Hermes** = harness that hosts every reasoning agent. Has a self-learning loop — agents log reusable skills to `skills_library` after every build, so the house gets sharper with every project.

**OpenClaw** = tool harness used by Hermes agents for mechanical work (file ops, API calls, deployments). Also hosts the pure-compute Backtester (no LLM).

**Paperclip** = orchestration layer. Routes tickets, tracks status, enforces gates.

---

## The 21 Agents

Each agent has a human first name so delegation feels natural (`Arthur assigned T-042 to Marcus` reads better than `PROJECT-MANAGER assigned T-042 to SENIOR-BACKEND-DEV`).

**Governance (1):** **Arthur** — Project Manager (Hermes PM, Opus 4.7). The only agent you talk to directly.

**Backend (2):** **Marcus** (Senior Backend Developer, Opus 4.7 advisor) → **Jack** (Backend Developer, Opus 4.6 executor).

**Frontend (2):** **Sonia** (Senior Frontend Developer, Opus 4.7) → **Leo** (Frontend Developer, Opus 4.6). Takes your JSX drafts and turns them into production components.

**Mobile (2):** **Dominic** (Senior Mobile Developer, Opus 4.7) → **Ellie** (Mobile Developer, Sonnet 4.6). RN, Swift, Kotlin.

**Mobile Design (2):** **Mira** (Senior Mobile Designer, Opus 4.7) → **Dante** (Mobile UI Developer, Kimi K2.6). Google Stitch for layouts, ChatGPT Image API for assets.

**DevOps (2):** **Viktor** (Senior DevOps, Opus 4.7, proactive) → **Theo** (DevOps Developer, Haiku 4.5). Hyperliquid co-location advisory built in.

**PineScript (3):** **Felix** (Senior PineScript Developer, Opus 4.7) → **Ben** (PineScript Developer, Opus 4.6) + **Clara** (Indicator Tester, Kimi K2.5). TradingView + Quantower.

**QA (3):** **Nadia** (Senior QA, Opus 4.7, merciless) → **Ivan** (QA, Kimi K2.5) + **Chloe** (Functional Tester, Kimi K2.5, Playwright MCP).

**Data (4):** **Henrik** (Senior Data Analyst, Opus 4.7) → **Elena** (Data Analyst, Sonnet 4.6) + **Oscar** (Senior Backtester, Opus 4.7, Karpathy autoresearch) → **Atlas** (Backtester, pure Python, no LLM).

---

## Pick Your Platform

| Platform | Prompt |
| --- | --- |
| Mac | [prompts/mac.md](prompts/mac.md) |
| Windows | [prompts/windows.md](prompts/windows.md) |
| Linux | [prompts/linux.md](prompts/linux.md) |

Open the file for your OS, copy everything below the horizontal rule, paste into Claude Code, hit Enter.

---

## What the Onboarding Agent Does

**Phase 1 — Environment check:** Confirms OS, Node.js, Git.

**Phase 2 — Intake interview (7 questions):**

1. House name
2. Default tech stack (Node/TS + Supabase | Python + Postgres | Rust + Postgres | Custom)
3. Build scope — MVP (core 9 agents, single-desk focus), Full (21 agents), or Custom
4. Target GitHub repo (or "create new")
5. Trading-specific features? (adds Hyperliquid/TradingView-aware defaults)
6. Anthropic and OpenRouter API keys
7. Supabase project URL and anon key

**Phase 3 — API key verification:** Tests Anthropic + OpenRouter keys.

**Phase 4 — Install Paperclip:** Runs `npx paperclipai onboard`, creates your house.

**Phase 5 — House directory:** Creates `~/[house-slug]/` with folders for agents, builds, plans, skills, logs, config.

**Phase 6 — Supabase schema:** Downloads `data/supabase-schema.sql` (~15 tables). Opens it for you to paste into Supabase SQL Editor, then sanity-checks via REST.

**Phase 7 — Fetch agent bundle:** Downloads `data/software-house-agents.json` — the single source of truth for all 21 agent definitions.

**Phase 8 — Hire the house:** Two-pass script. Pass 1 creates every agent in Paperclip via API, collects UUIDs. Pass 2 writes each agent's full AGENTS.md with the real UUIDs of their reports-to and supervisees embedded — so delegation commands work out of the box.

**Phase 9 — Open Paperclip:** Auto-opens your Paperclip workspace.

**Phase 10 — Verify + hand off:** Verifies every agent is wired correctly. Prints a house summary and the first PM message to send.

---

## What You'll Be Able to Do After Setup

- Drop a PRD + SDD + JSX front-end draft into the PM
- Watch the PM break it into tickets and route them to Senior Advisors
- See Senior Advisors write execution plans and hand off to Executors
- Get live progress updates as code ships through review, QA, functional testing
- Receive a post-mortem with reusable skills logged to `skills_library` after every build — so the next build starts with more capability than this one

---

## Requirements

- **Claude Code** — already running
- **Node.js** — prompt checks; opens download page if missing
- **Git** — prompt checks; opens download page if missing
- **Supabase** — free-tier account is enough
- **Anthropic API key** — for Hermes agents (Opus 4.7 advisors, Opus 4.6 / Sonnet 4.6 / Haiku 4.5 executors)
- **OpenRouter API key** — for Kimi K2.5 and K2.6 (testers and mobile UI)
- **Paperclip subscription or free tier**

---

## Repo Layout

```
software-house-repo/
├── README.md                           # this file
├── CONTRIBUTING.md                     # how to add/modify agents
├── LICENSE
├── manifest.yaml                       # master agent index
├── FLOW.md                             # end-to-end pipeline diagram
├── prompts/
│   ├── mac.md                          # paste-into-Claude-Code for macOS
│   ├── linux.md                        # paste-into-Claude-Code for Linux
│   └── windows.md                      # paste-into-Claude-Code for Windows
├── data/
│   ├── software-house-agents.json      # 21-agent definition bundle
│   └── supabase-schema.sql             # ~15 tables
├── scripts/
│   └── build_bundle.py                 # parses agents/*.md → JSON bundle
├── docs/
│   ├── KICKSTART.md                    # how to feed PRD+SDD+JSX in
│   ├── APPROVAL-FLOW.md                # PM → Senior → Executor → back-up loop
│   └── HERMES-SKILL-LIBRARY.md         # how the learning loop works
└── agents/                             # human-readable agent definitions
    ├── SCHEMA.md                       # agent file format spec
    ├── governance/
    ├── backend/
    ├── frontend/
    ├── mobile/
    ├── mobile-design/
    ├── devops/
    ├── pinescript/
    ├── qa/
    └── data/
```

You don't need to touch `data/` or `agents/` directly — the onboarding prompt fetches what it needs. `agents/` is there so you (or anyone auditing the repo) can read any agent's full definition without parsing JSON.

---

## Three Rules

1. **Only the PM talks to the user.** Senior Advisors and Executors never contact you directly. If a desk needs input, it escalates through the PM.
2. **Every build ends with a post-mortem.** Logged to `skills_library`. Skip it and the learning loop stops compounding.
3. **Executors never skip plans.** A ticket without a plan is a rejected ticket. Plan drift is the #1 source of rework.

---

## Credits

Structural inspiration from the Thesis House pattern. Software House adapts the same plug-and-play Paperclip architecture from a 36-agent investment research firm to a 21-agent software development shop, with the Brain/Hands operating model and Hermes self-learning loop.
