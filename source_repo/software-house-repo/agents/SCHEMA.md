# Software House — Agent Definition Schema

Each agent is a single Markdown file with YAML frontmatter. This format is designed for Paperclip ingestion: machine-readable fields up top for orchestration, human-readable sections below for prompt construction.

## File naming convention

`{desk}/{agent-id}.md` — e.g., `backend/senior-backend-dev.md`, `pinescript/indicator-tester.md`

Agent IDs are kebab-case, stable, and never reused. Paperclip uses the ID as the routing key.

## YAML frontmatter fields

```yaml
id: string                    # unique kebab-case identifier
name: string                  # display name in caps (e.g., SENIOR-BACKEND-DEV)
person_name: string           # human first name for the agent (e.g., Marcus, Nadia, Arthur)
desk: string                  # governance | backend | frontend | mobile | mobile-design | devops | pinescript | qa | data
runtime: string               # hermes | openclaw
model: string                 # claude-opus-4-7 | claude-opus-4-6 | claude-sonnet-4-6 | claude-haiku-4-5 | moonshotai/kimi-k2-6 | moonshotai/kimi-k2-5 | none
reports_to: string            # agent-id of supervisor (or "user" for Project Manager)
supervises: [string]          # list of agent-ids this agent supervises (empty array if none)
consumes_from: [string]       # upstream agents this receives input from
produces_for: [string]        # downstream agents this sends output to
triggers: [string]            # event types that activate this agent
frequency: string             # realtime | scheduled-{cron} | on-demand | continuous
priority: integer             # 1-5, where 1 is highest (affects queue ordering in Paperclip)
tools: [string]               # external tools/APIs the agent can call
storage: [string]             # Supabase tables this agent reads/writes
```

## Runtime assignment

- **hermes** — Agents that require reasoning, judgement, or creative output. These are the "brains." Hermes includes a self-learning skill library that compounds across projects. Typically assigned Opus 4.7 for Advisors, Opus 4.6 / Sonnet 4.6 / Kimi for Executors.
- **openclaw** — Agents that primarily call tools, transform data, or execute deterministic pipelines. These are the "hands." Used as infrastructure underneath Hermes agents for file ops, API calls, deployments. Also used as the runtime for pure-compute agents (e.g., Backtester) that need no LLM at all.

## The Brain / Hands pattern

Every specialist role in the house is split into two tiers:

| Tier | Role | Model | What it does |
|---|---|---|---|
| **Advisor** | Senior [Role] | Opus 4.7 via Hermes | Writes the plan. Reviews. Unblocks. Scarce resource — minimal token volume. |
| **Executor** | [Role] | Opus 4.6 / Sonnet 4.6 / Kimi / Haiku via Hermes | Follows the plan. Writes code/designs/configs. High token volume on cheaper models. |

**The escalation loop:** Advisor writes plan → Executor runs it → stuck? → back to Advisor → Advisor clarifies → Executor continues.

No "juniors." The Executor is a competent engineer, not an entry-level coder. The naming is deliberate: Senior Backend Developer + Backend Developer, not Senior + Junior.

## Markdown sections (required, in order)

### `## Personality`
Character, voice, disposition. 100–200 words. This shapes how the agent writes, reasons, and presents its output. Every agent has a distinct personality because uniform agents produce uniform (boring, groupthink-prone) output.

### `## Role`
One-paragraph mandate. What this agent is accountable for. Mirror of the org-chart description.

### `## Inputs`
Structured list of what this agent receives. Format, source, trigger.

### `## Outputs`
Structured list of what this agent produces. Format, destination, schema.

### `## Skills`
Numbered list of specific capabilities. Each skill is a sentence or two. These are what Paperclip uses to match tasks to agents.

### `## Rules of Engagement`
Explicit do's and don'ts. Hard constraints on behaviour.

### `## Failure Modes`
Known ways this agent can fail and how to recognise them. Used by the governance layer (Project Manager, Senior QA) to audit agent output.

### `## Prompt Stub`
The opening lines of the system prompt used when this agent runs. Paperclip composes the full prompt by combining this stub with runtime context (current ticket, plan, PR diff, etc.).
