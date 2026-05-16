#!/usr/bin/env python3
"""
Convert Pantheon V8.3 payload to agentcompanies/v1 directory tree.
V8.5: uniform hermes_local adapter, per-agent HERMES_HOME.

Reads: Pantheon/paperclip/organization.import.json (canonical source)
       Pantheon/skills/hermes_seed/*.md           (seed skills)
       Pantheon/company/*.yaml                    (governance policies)
       Pantheon/policies/*.md                     (operating rules)

Writes: pantheon/                                (importable package)
         COMPANY.md
         README.md
         LICENSE
         .paperclip.yaml
         agents/<slug>/AGENTS.md
         skills/<slug>/SKILL.md

The .paperclip.yaml emits the hermes_local adapter for every agent, with the
agent's model passed through (provider/model) and a per-agent HERMES_HOME
env var (~/.hermes-<slug>). Owen is intentionally skipped (NotebookLM has
no API). The hermes_local adapter is provided by hermes-paperclip-adapter
and loaded via Paperclip's external adapter plugin system
(~/.paperclip/adapter-plugins.json).

Reference: https://agentcompanies.io/specification
           https://github.com/NousResearch/hermes-paperclip-adapter
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SH = ROOT / "Pantheon"
OUT = ROOT / "pantheon"

# V8.5: uniform hermes_local adapter for every agent.
# hermes_local is provided by the hermes-paperclip-adapter npm package,
# loaded via Paperclip's external adapter plugin loader (~/.paperclip/adapter-plugins.json).
# Each agent gets its own HERMES_HOME via the adapter env: pass-through, giving
# 32 distinct identities (Owen skipped — null model, no API).
#
# This map resolves a V8.3 model prefix to the Hermes "provider" field, which
# tells Hermes which API to use. The "model" field is the V8.3 model string
# (provider/model format) passed through unchanged.
HERMES_PROVIDER_MAP = {
    "anthropic/":  "auto",          # Hermes auto-detects Anthropic native
    "openai/":     "openai-codex",  # Codex/OpenAI native
    "google/":     "openrouter",    # No native Google in Hermes — use OpenRouter
    "deepseek/":   "openrouter",    # No native DeepSeek — use OpenRouter
    "moonshotai/": "kimi-coding",   # Hermes has a native Kimi/Moonshot provider
}

# Retained from V8.4 for backward compatibility (rendered in skill bodies,
# legacy display strings). Not used in adapter emission.
ADAPTER_MAP_LEGACY = {
    "anthropic/": ("claude_local", "claude-opus-4-7"),
    "openai/":    ("codex_local", "gpt-5-mini"),
    "google/":    ("gemini_local", "gemini-3.1-pro"),
    "deepseek/":  ("codex_local", "gpt-5-mini"),
    "moonshotai/": ("codex_local", "gpt-5-mini"),
}
ADAPTER_MAP = ADAPTER_MAP_LEGACY  # kept as alias; do not use in V8.5 emit path

# Anthropic model id mapping from V8.3 strings to Anthropic API ids
ANTHROPIC_MODEL_MAP = {
    "anthropic/claude-opus-4.7":       "claude-opus-4-7",
    "anthropic/claude-opus-4.7-xhigh": "claude-opus-4-7",
    "anthropic/claude-opus-4.7-max":   "claude-opus-4-7",
    "anthropic/claude-sonnet-4.6":     "claude-sonnet-4-6",
    "anthropic/claude-3.5-haiku":      "claude-3-5-haiku-latest",
}

OPENAI_MODEL_MAP = {
    "openai/gpt-5-mini":       "gpt-5-mini",
    "openai/gpt-5.5":          "gpt-5.5",
    "openai/gpt-5.5-thinking": "gpt-5.5",
}

GOOGLE_MODEL_MAP = {
    "google/gemini-3.1-pro": "gemini-3.1-pro",
}


def slugify(s):
    """Convert agent id to a clean directory slug."""
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def map_adapter(model):
    """V8.4 compat shim: return (adapter_type, adapter_model_id).
    V8.5 emit path uses map_hermes() instead — kept so legacy callers don't break.
    """
    if model is None:
        return None, None
    for prefix, (adapter, _default) in ADAPTER_MAP_LEGACY.items():
        if model.startswith(prefix):
            if model in ANTHROPIC_MODEL_MAP:
                return adapter, ANTHROPIC_MODEL_MAP[model]
            if model in OPENAI_MODEL_MAP:
                return adapter, OPENAI_MODEL_MAP[model]
            if model in GOOGLE_MODEL_MAP:
                return adapter, GOOGLE_MODEL_MAP[model]
            return adapter, model.split("/", 1)[1]
    return None, None


def map_hermes(model):
    """V8.5: return (model_id_for_hermes, provider) tuple.
    model_id_for_hermes is the provider/model format Hermes expects.
    Provider is one of: auto, openrouter, nous, openai-codex, zai, kimi-coding,
    minimax, minimax-cn (from hermes-paperclip-adapter README).
    """
    if model is None:
        return None, None
    for prefix, provider in HERMES_PROVIDER_MAP.items():
        if model.startswith(prefix):
            # Pass the V8.3 model string through unchanged — Hermes accepts
            # provider/model format directly.
            return model, provider
    return None, None


def yaml_str(s):
    """Quote a string for YAML if it contains special characters."""
    if s is None:
        return "null"
    if isinstance(s, bool):
        return "true" if s else "false"
    s = str(s)
    if not s:
        return '""'
    # If safe identifier, no quoting needed
    if re.match(r"^[a-zA-Z0-9_./-]+$", s) and s not in {"true", "false", "null", "yes", "no"}:
        return s
    # Escape and quote
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_company_md():
    """Write COMPANY.md from the org + governance policies."""
    org = json.loads((SH / "paperclip" / "organization.import.json").read_text(encoding="utf-8"))
    company = org.get("organization", {})

    # Pull governance policies from YAML files
    approval_yaml = (SH / "company" / "approval_policy.yaml").read_text(encoding="utf-8")
    budget_yaml = (SH / "company" / "budget_policy.yaml").read_text(encoding="utf-8")

    name = company.get("display_name") or "Pantheon"
    description = company.get("description") or company.get("ethos") or \
        "AI-native software studio for building financial-market systems with architecture-first, test-first, security-aware execution."

    body = f"""---
schema: agentcompanies/v1
name: {yaml_str(name)}
slug: pantheon
description: {yaml_str(description[:200])}
version: 8.4.0
license: MIT
authors:
  - name: Bobby
goals:
  - Ship financial-market systems with architecture-first, test-first execution
  - Maintain a hermes-only standard harness with rigorous typed handoffs
  - Enforce human approval for governance, merge, deploy, and production trading changes
  - Compound trading edge, content output, and infrastructure leverage
tags:
  - software
  - trading
  - infrastructure
  - financial
  - autonomous
---

# Pantheon

AI-native software studio for building groundbreaking financial-market systems. Architecture-first. Test-first. Security-aware. Human approval for governance, merge, deploy, production trading changes, and API-key permissions.

## Workflow

This is a **pipeline** organization with a hub-and-spoke escalation layer. Work moves through:

```
Context Pack -> PRD -> SDD -> Tickets -> TDD -> Implementation -> PR Review -> Merge Gate -> Memory Update
```

Arthur is the Project Manager and head employee. Arthur routes PRDs to the appropriate Senior owner by technical domain (backend, frontend, mobile, Pine Script, Quantower/C#, DevOps, QA). Seniors break PRDs into SDDs, tickets, and red tests. Junior developers implement. Cody reviews PRs. Maxwell handles staff-level escalation. Magnus owns principal architecture rethinks. Winston archives final artifacts and learning.

## Hard rules

- Context pack before non-trivial work.
- Architecture before tickets.
- Tests before code.
- Green before next task.
- Green and reviewed before merge.
- Human approval for governance, merge, deployment, production trading rules, and API-key permission changes.
- No production trading keys in general workers.
- Execution cannot invent trades.
- Automated sizing must use fractional Kelly only.

## Org chart

| Slug | Name | Role | Reports to |
|---|---|---|---|
| arthur | Arthur | Project Manager / Head | (none — board) |
| marcus | Marcus | Senior Backend Developer | arthur |
| jack | Jack | Backend Developer | marcus |
| sonia | Sonia | Senior Frontend Developer | arthur |
| leo | Leo | Frontend Developer | sonia |
| dominic | Dominic | Senior Mobile Developer | arthur |
| ellie | Ellie | Mobile Developer | dominic |
| dante | Dante | Mobile UI Developer | mira |
| mira | Mira | Senior Mobile Designer | arthur |
| viktor | Viktor | Senior DevOps | arthur |
| theo | Theo | DevOps Developer | viktor |
| felix | Felix | Senior PineScript Developer | arthur |
| ben | Ben | PineScript Developer | felix |
| nathan | Nathan | Senior Quantower/C# Architect | arthur |
| grant | Grant | Quantower/C# Automation Developer | nathan |
| nadia | Nadia | Senior QA | arthur |
| ivan | Ivan | QA | nadia |
| chloe | Chloe | Functional Tester | nadia |
| henrik | Henrik | Senior Data Analyst | arthur |
| elena | Elena | Data Analyst | henrik |
| oscar | Oscar | Senior Backtester | henrik |
| clara | Clara | Claude PR Review Lead | arthur |
| cody | Cody | Code Escalation Reviewer | arthur |
| maxwell | Maxwell | Staff Escalation Engineer | arthur |
| magnus | Magnus | Principal Solution Architect | arthur |
| priya | Priya | System Architect | arthur |
| safiya | Safiya | Security Reviewer | arthur |
| winston | Winston | Director of Knowledge Architecture | arthur |
| owen | Owen | Research Pack Agent | arthur |
| vera | Vera | API Bottleneck Intelligence Agent | arthur |
| graham | Graham | Feasibility Strategist | arthur |
| stone | Stone | Skeptical Validation Agent | arthur |
| adrian | Adrian | Opportunity Architect | arthur |

## Approval policy summary

The full approval policy is in `.paperclip.yaml.governance`. Highlights:

- Human board approval required for: governance file changes, production trading rule changes, API key permission changes, budget increases, tool permission expansion, autonomous routine creation, merge to main, production deploy, trading execution logic changes.
- Auto-allowed (when policy passes): create context packs, draft PRDs/SDDs/test plans, write proposed memory updates, stage import payloads.

## Budget summary

- Default monthly cap: $300 USD
- Warning at 70%, hard stop at 100%
- Per-agent caps: see `.paperclip.yaml` and `budget_policy.yaml` reference

## Getting started

```bash
paperclipai company import ./pantheon --target new --new-company-name "Pantheon" --include company,agents,skills --dry-run
```

Drop the `--dry-run` once the preview looks right.

## References

- [Agent Companies specification](https://agentcompanies.io/specification)
- [Paperclip](https://github.com/paperclipai/paperclip)
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) (optional adapter)
"""
    (OUT / "COMPANY.md").write_text(body, encoding="utf-8")
    print(f"  wrote COMPANY.md")


def write_readme():
    body = """# Pantheon — Paperclip company package

This is the importable `agentcompanies/v1` package for the Pantheon organization. It contains:

- `COMPANY.md` — company metadata, goals, hard rules, org chart
- `agents/<slug>/AGENTS.md` — one per agent (33 total)
- `skills/<slug>/SKILL.md` — seed skills attached to agents
- `.paperclip.yaml` — Paperclip vendor extension mapping models to adapters

## Import

```bash
# Preview
paperclipai company import . --target new --new-company-name "Pantheon" --include company,agents,skills --dry-run

# Apply
paperclipai company import . --target new --new-company-name "Pantheon" --include company,agents,skills --yes
```

## Prerequisites

1. Paperclip installed and running locally (`npx paperclipai onboard --yes` then `pnpm paperclipai run`).
2. The CLI adapters Paperclip will invoke must be present on the same machine:
   - `claude_local` → Claude Code CLI
   - `codex_local` → Codex CLI
   - `gemini_local` → Gemini CLI
3. Each CLI must have its provider API key configured.

## Adapter mapping summary

| Model family | Paperclip adapter | Reasoning |
|---|---|---|
| anthropic/claude-* | claude_local | Native Claude Code CLI |
| openai/gpt-* | codex_local | Codex CLI |
| google/gemini-* | gemini_local | Gemini CLI |
| deepseek/* | codex_local + OpenRouter | No native deepseek adapter |
| moonshotai/kimi-* | codex_local + OpenRouter | No native kimi adapter |

Owen's model is intentionally unassigned (`null`) because NotebookLM is a manual product, not an API model. Paperclip will skip his runtime adapter; resolve when (a) NotebookLM exposes an API, or (b) the workflow moves to Gemini 3.1 Pro.

## Hermes integration (optional)

This package does not require Hermes. If you want Hermes as a per-agent runtime, the cleanest pattern is:

1. Install Hermes once per agent identity that needs its own SOUL/memory: `HERMES_HOME=~/.hermes-arthur hermes init`, etc.
2. Configure each Hermes instance's `~/.hermes-<slug>/config.yaml` with the right provider and `skills.external_dirs` pointing to the matching `skills/<slug>/` directory.
3. Wrap each Hermes CLI invocation in a custom Paperclip adapter (Paperclip supports custom adapters via plugins).

For an out-of-the-box install, the native Paperclip adapters above are sufficient. Hermes is a Phase 2 upgrade.

## References

- [Agent Companies specification](https://agentcompanies.io/specification)
- [Paperclip](https://github.com/paperclipai/paperclip)
"""
    (OUT / "README.md").write_text(body, encoding="utf-8")
    print(f"  wrote README.md")


def write_license():
    body = """MIT License

Copyright (c) 2026 Bobby

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    (OUT / "LICENSE").write_text(body, encoding="utf-8")
    print(f"  wrote LICENSE")


# Deterministic short slugs for each canonical agent id
SHORT_SLUG = {
    "arthur-project-manager": "arthur",
    "marcus-senior-backend-developer": "marcus",
    "jack-backend-developer": "jack",
    "senior-frontend-dev": "sonia",
    "frontend-dev": "leo",
    "senior-mobile-dev": "dominic",
    "mobile-dev": "ellie",
    "mobile-ui-dev": "dante",
    "senior-mobile-designer": "mira",
    "senior-devops": "viktor",
    "devops-dev": "theo",
    "felix-senior-pinescript-developer": "felix",
    "ben-pinescript-developer": "ben",
    "nathan-senior-quantower-csharp-architect": "nathan",
    "grant-quantower-csharp-automation-developer": "grant",
    "senior-qa": "nadia",
    "qa": "ivan",
    "functional-tester": "chloe",
    "senior-data-analyst": "henrik",
    "data-analyst": "elena",
    "senior-backtester": "oscar",
    "clara-claude-pr-review-lead": "clara",
    "cody-code-escalation-reviewer": "cody",
    "maxwell-staff-escalation-engineer": "maxwell",
    "magnus-principal-solution-architect": "magnus",
    "system-architect": "priya",
    "security-reviewer": "safiya",
    "winston-director-knowledge-architecture": "winston",
    "owen-research-pack-agent": "owen",
    "vera-api-bottleneck-intelligence-agent": "vera",
    "graham-feasibility-strategist": "graham",
    "stone-skeptical-validation-agent": "stone",
    "adrian-opportunity-architect": "adrian",
}

# Reporting structure derived from V8.3 manifest + role hierarchy
REPORTS_TO = {
    "arthur": None,  # head of company
    "marcus": "arthur",
    "jack": "marcus",
    "sonia": "arthur",
    "leo": "sonia",
    "dominic": "arthur",
    "ellie": "dominic",
    "mira": "arthur",
    "dante": "mira",
    "viktor": "arthur",
    "theo": "viktor",
    "felix": "arthur",
    "ben": "felix",
    "nathan": "arthur",
    "grant": "nathan",
    "nadia": "arthur",
    "ivan": "nadia",
    "chloe": "nadia",
    "henrik": "arthur",
    "elena": "henrik",
    "oscar": "henrik",
    "clara": "arthur",
    "cody": "arthur",
    "maxwell": "arthur",
    "magnus": "arthur",
    "priya": "arthur",
    "safiya": "arthur",
    "winston": "arthur",
    "owen": "arthur",
    "vera": "arthur",
    "graham": "arthur",
    "stone": "arthur",
    "adrian": "arthur",
}


def write_agents():
    org = json.loads((SH / "paperclip" / "organization.import.json").read_text(encoding="utf-8"))
    agents_dir = OUT / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for a in org.get("agents", []):
        aid = a.get("id")
        slug = SHORT_SLUG.get(aid)
        if not slug:
            print(f"  WARN: no slug mapping for {aid}, skipping")
            continue

        name = a.get("name") or slug
        role = a.get("role") or "Specialist"
        description = (a.get("description") or "").strip()
        personality = (a.get("personality") or "").strip()
        skills_csv = a.get("skills") or ""
        skills_list = [s.strip() for s in re.split(r"[,\n]", skills_csv) if s.strip()]
        responsibility = (a.get("responsibility") or "").strip()
        reports_to = REPORTS_TO.get(slug)

        # Get seed skill content if present
        seed_path = a.get("seed_skill_path") or ""
        skill_slug = f"{slug}-seed"

        # Smart-truncate description at sentence or word boundary, max ~200 chars
        if description:
            desc_short = description[:240]
            # Prefer to end at a sentence boundary within the first 200 chars
            sentence_end = max(desc_short[:200].rfind(". "), desc_short[:200].rfind("! "), desc_short[:200].rfind("? "))
            if sentence_end > 80:
                desc_short = description[:sentence_end + 1]
            else:
                # Fall back to word boundary near 180
                word_end = desc_short[:180].rfind(" ")
                desc_short = desc_short[:word_end] + "..." if word_end > 80 else desc_short[:180]
        else:
            desc_short = role

        # Frontmatter for AGENTS.md
        front_lines = [
            "---",
            "schema: agentcompanies/v1",
            f"name: {yaml_str(name)}",
            f"slug: {slug}",
            f"title: {yaml_str(role)}",
            f"description: {yaml_str(desc_short)}",
        ]
        if reports_to is None:
            front_lines.append("reportsTo: null")
        else:
            front_lines.append(f"reportsTo: {reports_to}")
        front_lines.append(f"skills:")
        front_lines.append(f"  - {skill_slug}")
        front_lines.append("---")

        # Body
        body_lines = [
            f"# {name} — {role}",
            "",
            "## Role",
            "",
            description if description else f"{name} is the {role} in the Pantheon.",
            "",
        ]

        if personality and personality.strip().lower() not in ("", "atlas is the name of the backtest harness"):
            body_lines.extend([
                "## Personality",
                "",
                personality,
                "",
            ])

        if responsibility:
            body_lines.extend([
                "## Responsibility",
                "",
                responsibility,
                "",
            ])

        # Workflow context based on role
        body_lines.append("## Workflow position")
        body_lines.append("")
        if slug == "arthur":
            body_lines.extend([
                "You are the Project Manager and Head employee. You receive PRDs from the board (the user) and route them to the appropriate Senior owner by technical domain.",
                "",
                "**Where work comes from:** new PRDs in `workspace/01_PRDs/`, escalations from Seniors, user-initiated approvals.",
                "**What you produce:** routing decisions, escalation packets, merge gates, MASTER_STATUS updates, hiring packets when specialists are needed.",
                "**Who you hand off to:** the Senior owner of the relevant domain (Marcus, Sonia, Dominic, Felix, Nathan, Viktor, Nadia, Henrik) for engineering; Owen for research intake; Winston for archival.",
                "**Hard rule:** if confidence is low, route to the assigned Senior or the user. Do not guess. Do not silently expand the team. Do not bypass human approval for governance, merge, deploy, or production trading changes.",
                "",
            ])
        elif slug in {"marcus", "sonia", "dominic", "felix", "nathan", "viktor", "nadia", "henrik", "mira"}:
            body_lines.extend([
                f"You are a Senior owner. Arthur routes PRDs to you when they fall in your technical domain.",
                "",
                f"**Where work comes from:** PRDs routed by Arthur, escalations from your standard developer after 7-10 attempts.",
                f"**What you produce:** SDDs, feature tickets, red TDD tests, plan reviews, final commits for your lane.",
                f"**Who you hand off to:** your standard developer for implementation; Maxwell if you exhaust 3 diagnosis attempts; Cody for review; Arthur for merge gating.",
                f"**Hard rule:** architecture before tickets, tests before code. No merge without green CI + reviewer approval.",
                "",
            ])
        elif slug in {"jack", "leo", "ellie", "ben", "grant", "theo", "ivan", "elena", "dante"}:
            body_lines.extend([
                f"You are a standard developer. You execute the tickets your Senior writes.",
                "",
                "**Where work comes from:** feature tickets + red tests from your Senior, with a context pack from Winston.",
                "**What you produce:** implementations, passing tests, PR-ready branches, blocker packets when stuck.",
                "**Who you hand off to:** your Senior after a passing test or after 7-10 failed self-fix attempts; Cody for PR review.",
                "**Hard rule:** work only inside the assigned project namespace. Strict SDD alignment. Self-fix 7-10 attempts before escalating.",
                "",
            ])
        elif slug == "winston":
            body_lines.extend([
                "You are the Director of Knowledge Architecture. You build context packs and archive final artifacts.",
                "",
                "**Where work comes from:** context_pack_requested events, completed work products from Arthur.",
                "**What you produce:** context packs (per `context_pack.schema.json`), memory updates (per `memory_update.schema.json`), weekly memory hygiene reports.",
                "**Who you hand off to:** Arthur for routing context packs to the active project, the board for governance-affecting memory updates.",
                "**Hard rule:** governance-affecting memory updates require human approval. Archive only final artifacts and real lessons, not retry spam.",
                "",
            ])
        elif slug == "cody":
            body_lines.extend([
                "You are the code escalation reviewer. You audit implementations and PRs.",
                "",
                "**Where work comes from:** PR review requests, escalation at attempt 18, fanout reviews on high-risk PRs.",
                "**What you produce:** merge_review verdicts (per `merge_review.schema.json`), forensic reports on architecture-level failures, CI triage summaries.",
                "**Who you hand off to:** the Senior owner with required actions, Arthur for merge gating, Magnus if failure is architecture-level.",
                "**Hard rule:** do not approve merges with red CI or unresolved policy violations.",
                "",
            ])
        elif slug == "maxwell":
            body_lines.extend([
                "You are the staff escalation engineer. You handle deep failures at attempts 16-17.",
                "",
                "**Where work comes from:** Senior tactical fixes exhausted (attempts 13-15 failed).",
                "**What you produce:** minimal viable fix paths, cross-file diagnosis, dependency/config corrections.",
                "**Who you hand off to:** Arthur (who routes the fix back to the standard developer), Cody if forensic review is needed.",
                "**Hard rule:** ignore surface errors; find deep cross-file logic rot, config failure, or architecture-to-test mismatch.",
                "",
            ])
        elif slug == "magnus":
            body_lines.extend([
                "You are the Principal Solution Architect. You handle architecture rethink at attempt 19.",
                "",
                "**Where work comes from:** Cody forensic review concluded the failure is architecture-level.",
                "**What you produce:** 1-3 entirely new structural pathways, approach qualification reports.",
                "**Who you hand off to:** Arthur (never directly to a junior). Arthur routes your approach to the Senior, who rewrites the plan.",
                "**Hard rule:** terminate the automated loop and await manual review when proposing a new architecture.",
                "",
            ])
        elif slug == "clara":
            body_lines.extend([
                "You are the Claude PR Review Lead. First-line deep PR review.",
                "",
                "**Where work comes from:** opened PRs in the dual-review pipeline.",
                "**What you produce:** merge_review verdicts (per `merge_review.schema.json`) with `review_type: claude_pr`.",
                "**Who you hand off to:** Cody for second-line Codex review; Arthur for merge gating.",
                "**Hard rule:** read code against PRD intent + SDD alignment, not just style.",
                "",
            ])
        elif slug in {"owen", "vera", "graham", "stone", "adrian"}:
            body_lines.extend([
                f"You are part of the PRD research/intake pipeline. You operate before engineering.",
                "",
                "**Where work comes from:** new PRD intake requests from Arthur.",
                "**What you produce:** research packs (Owen), API/bottleneck reports (Vera), feasibility reports (Graham), skeptical validation (Stone), opportunity shaping (Adrian).",
                "**Who you hand off to:** Arthur for user approval gate, then routing to engineering.",
                "**Hard rule:** do not decide feasibility or opportunity unilaterally. Produce structured outputs the user approves.",
                "",
            ])
        elif slug == "priya":
            body_lines.extend([
                "You are the System Architect. You handle cross-cutting design and validation.",
                "",
                "**Where work comes from:** Arthur activates you when architecture review or system-level design is needed.",
                "**What you produce:** architecture council outputs, design validation reports.",
                "**Who you hand off to:** Arthur for routing.",
                "",
            ])
        elif slug == "safiya":
            body_lines.extend([
                "You are the Security Reviewer. You assess security risks.",
                "",
                "**Where work comes from:** Arthur activates you for security-sensitive PRs, trading system red-team reviews, or API-key changes.",
                "**What you produce:** merge_review verdicts with `review_type: security`, security gap reports.",
                "**Who you hand off to:** Arthur for merge gating.",
                "**Hard rule:** production trading keys forbidden in general workers. API key permission changes require board approval.",
                "",
            ])
        elif slug == "chloe":
            body_lines.extend([
                "You are the Functional Tester. You run end-to-end functional tests.",
                "",
                "**Where work comes from:** Nadia (Senior QA) assigns functional test plans.",
                "**What you produce:** test results, regression reports.",
                "**Who you hand off to:** Nadia for test plan review.",
                "",
            ])
        elif slug == "oscar":
            body_lines.extend([
                "You are the Senior Backtester. You design backtests for trading strategies.",
                "",
                "**Where work comes from:** Henrik (Senior Data Analyst) or Arthur for strategy validation.",
                "**What you produce:** backtest plans, performance metrics, strategy validation reports.",
                "**Who you hand off to:** Henrik, Arthur. Atlas (backtest harness) is the deterministic Python compute layer Oscar designs experiments for.",
                "**Hard rule:** fractional Kelly only for any sizing recommendation. Execution cannot invent trades.",
                "",
            ])
        elif skills_list:
            body_lines.extend([
                f"## Core skills",
                "",
                "\n".join(f"- {s}" for s in skills_list[:8]),
                "",
            ])

        # Execution contract (from company-creator skill spec)
        body_lines.extend([
            "## Execution contract",
            "",
            "- Start actionable work in the same heartbeat. Do not stop at a plan unless planning was requested.",
            "- Leave durable progress in comments, work products, or documents with the next action.",
            "- Use child issues for long or parallel delegated work instead of polling.",
            "- Mark blocked work with the unblock owner and action.",
            "- Respect budget, pause/cancel, approval gates, and company boundaries.",
            "",
        ])

        text = "\n".join(front_lines) + "\n\n" + "\n".join(body_lines)
        agent_dir = agents_dir / slug
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / "AGENTS.md").write_text(text, encoding="utf-8")
        count += 1

    print(f"  wrote {count} AGENTS.md files")


def write_skills():
    """Convert each Hermes seed skill to an agentskills.io SKILL.md."""
    org = json.loads((SH / "paperclip" / "organization.import.json").read_text(encoding="utf-8"))
    skills_dir = OUT / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    seed_root = SH / "skills" / "hermes_seed"

    count = 0
    for a in org.get("agents", []):
        aid = a.get("id")
        slug = SHORT_SLUG.get(aid)
        if not slug:
            continue

        seed_path = a.get("seed_skill_path")
        if not seed_path:
            continue
        full_path = SH / seed_path
        if not full_path.exists():
            # Try the hermes_seed directory by convention
            alt = seed_root / f"skill_{aid}_seed.md"
            if alt.exists():
                full_path = alt
            else:
                print(f"  WARN: no seed skill found for {aid}")
                continue

        skill_slug = f"{slug}-seed"
        skill_dir = skills_dir / skill_slug
        skill_dir.mkdir(parents=True, exist_ok=True)

        body = full_path.read_text(encoding="utf-8")
        # Strip any pre-existing frontmatter
        body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", body, count=1, flags=re.S)

        # Canonicalize legacy model strings — V8.3 seed skills still carry
        # phrases like "OPS 4.7 High under Hermes" / "DeepSeek V4 Pro under Hermes"
        # in the body. Replace with the actual model id used by Paperclip's adapter.
        model = a.get("model")
        if model and "OPS 4.7" in body:
            replacement = f"`{model}`"
            body = re.sub(r"OPS 4\.7\s+(Extra High|High|Max|X High|xhigh|max)?\s*under Hermes\.?",
                          replacement + " under Hermes.", body, flags=re.I)
            body = body.replace("OPS 4.7 under Hermes.", replacement + " under Hermes.")
        if model and "DeepSeek V4 Pro under Hermes" in body:
            body = body.replace("DeepSeek V4 Pro under Hermes", f"`{model}` under Hermes")
        if model and "Gemini Pro 3.1 under Hermes" in body:
            body = body.replace("Gemini Pro 3.1 under Hermes", f"`{model}` under Hermes")
        if model and "GPT-5.5 under Hermes" in body:
            body = body.replace("GPT-5.5 under Hermes", f"`{model}` under Hermes")

        front = f"""---
name: {skill_slug}
description: Seed skill for {slug} ({a.get('role','')}) — operational procedures, escalation rules, and handoff conventions.
version: 1.0.0
metadata:
  hermes:
    tags: [pantheon, {slug}]
    category: organizational
---

"""
        (skill_dir / "SKILL.md").write_text(front + body, encoding="utf-8")
        count += 1

    print(f"  wrote {count} SKILL.md files")


def write_paperclip_yaml():
    """Generate .paperclip.yaml — the Paperclip vendor extension."""
    org = json.loads((SH / "paperclip" / "organization.import.json").read_text(encoding="utf-8"))

    lines = [
        "schema: paperclip/v1",
        "agents:",
    ]

    gh_agents = {"jack", "marcus", "leo", "sonia", "ellie", "dominic", "ben", "felix",
                 "grant", "nathan", "theo", "viktor", "cody", "clara", "maxwell"}

    for a in org.get("agents", []):
        aid = a.get("id")
        slug = SHORT_SLUG.get(aid)
        if not slug:
            continue

        model = a.get("model")
        effort = a.get("effort")  # 'xhigh' or 'max' for Opus tiers
        hermes_model, provider = map_hermes(model)

        # Owen (slug=owen) has null model — keep agent record, omit adapter block.
        # Skipped at import; Paperclip will show the agent without a runtime.
        # See PATCH_NOTES_V8_5.md ("Owen decision") and manifest.json.hermes_local_adapter.skipped_agents.
        if model is None:
            lines.append(f"  {slug}:")
            lines.append(f"    # model unassigned: {a.get('model_unassigned_reason', 'no model available')}")
            lines.append(f"    # paperclip will skip the runtime adapter until a model is assigned")
            lines.append(f"    # (NotebookLM has no API; resolve when Gemini 3.1 Pro replaces it or NotebookLM exposes one)")
            continue

        # Unknown provider — skip rather than emit a broken block.
        if hermes_model is None or provider is None:
            lines.append(f"  {slug}:")
            lines.append(f"    # model {model} not in HERMES_PROVIDER_MAP — adapter block omitted")
            continue

        lines.append(f"  {slug}:")
        lines.append(f"    adapter:")
        lines.append(f"      type: hermes_local")
        lines.append(f"      config:")
        lines.append(f"        model: {hermes_model}")
        lines.append(f"        provider: {provider}")
        lines.append(f"        toolsets: terminal,file,web,browser,code_execution,mcp")
        lines.append(f"        timeoutSec: 300")
        lines.append(f"        graceSec: 10")
        lines.append(f"        quiet: true")
        # extraArgs is the right place for effort hints if Hermes supports them.
        # Hermes accepts --effort for some providers (Anthropic xhigh/max);
        # safe to pass — Hermes ignores unknown flags rather than failing.
        if effort:
            lines.append(f"        extraArgs:")
            lines.append(f"          - \"--effort\"")
            lines.append(f"          - \"{effort}\"")
        lines.append(f"        env:")
        lines.append(f"          HERMES_HOME: ~/.hermes-{slug}")
        # GitHub-touching agents: pass GH_TOKEN through to the Hermes process.
        # Paperclip resolves the secret at dispatch time.
        if slug in gh_agents:
            lines.append(f"          GH_TOKEN: ${{secrets.GH_TOKEN}}")
            lines.append(f"    inputs:")
            lines.append(f"      env:")
            lines.append(f"        GH_TOKEN:")
            lines.append(f"          kind: secret")
            lines.append(f"          requirement: optional")

    lines.append("")
    lines.append("# Governance policies (read by Paperclip on import)")
    lines.append("governance:")
    lines.append("  human_approval_required:")
    for item in [
        "governance_file_change",
        "production_trading_rule_change",
        "api_key_permission_change",
        "budget_increase",
        "tool_permission_expansion",
        "autonomous_routine_creation",
        "merge_to_main",
        "production_deploy",
        "trading_execution_logic_change",
    ]:
        lines.append(f"    - {item}")

    lines.append("")
    lines.append("budget:")
    lines.append("  default_monthly_cap_usd: 300")
    lines.append("  warning_threshold_pct: 70")
    lines.append("  hard_stop_threshold_pct: 100")
    lines.append("  hard_stop_action: pause_agent_and_escalate_to_arthur_then_human_board")
    lines.append("  per_agent_caps_usd:")
    for s, cap in [
        ("arthur", 25), ("jack", 35), ("marcus", 45), ("maxwell", 60),
        ("cody", 50), ("magnus", 60), ("winston", 20),
    ]:
        lines.append(f"    {s}: {cap}")

    (OUT / ".paperclip.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote .paperclip.yaml")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    print(f"Generating agentcompanies/v1 package at {OUT}")
    write_company_md()
    write_readme()
    write_license()
    write_agents()
    write_skills()
    write_paperclip_yaml()
    print(f"\nDone. Package ready at: {OUT}")
    print(f"Import with: paperclipai company import {OUT.name} --target new --new-company-name 'Pantheon' --include company,agents,skills --dry-run")


if __name__ == "__main__":
    main()
