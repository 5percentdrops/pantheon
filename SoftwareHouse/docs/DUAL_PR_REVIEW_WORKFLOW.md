# Dual PR Review Workflow

## Flow

PRD
→ SDD
→ System Architect
→ tests
→ implementation
→ PR opened/submitted
→ Clara — Claude PR Review Lead
→ Cody — Hermes Codex PR Reviewer
→ Safiya / Priya / Nadia conditional escalation
→ Arthur — Project Manager merge readiness

## Why two reviewers?
Clara provides the first-line deep PR review using Hermes + Claude Code Review / Opus 4.7.

Cody provides a second-model-family pass using Hermes + Codex, focusing on codebase reasoning, runnable fixes, test gaps, and recurring pattern learning.

## No third generic reviewer
There is no third general PR reviewer.
Specialists only receive escalations when triggered.
