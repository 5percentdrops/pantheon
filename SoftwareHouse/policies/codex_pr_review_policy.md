# Hermes Codex PR Review Policy

## Rule
Every implementation pull request must pass the Hermes Codex PR review gate before merge readiness.

## Correct architecture
- Harness: Hermes
- Underlying code-review engine/tool: latest available OpenAI Codex coding model
- Preferred Codex model when explicitly configurable: GPT-5.2-Codex
- Fallback: latest Codex default exposed by the local/web/CLI Codex environment

## Why Hermes is the harness
Hermes must learn from:
- recurring PR defects
- repeated missing tests
- repeated security issues
- recurring architecture drift
- common successful fixes
- new code patterns
- post-merge outcomes

## Placement in workflow
PRD
→ SDD
→ System Architect
→ tests
→ implementation
→ PR opened/submitted
→ Cody — Hermes Codex PR Reviewer
→ Senior QA / Security / Architecture as needed
→ Arthur — Project Manager merge readiness

## Invocation
Use whichever Codex path exists locally:
- automatic Codex PR review if enabled for the GitHub repo
- `@codex review`
- `@codex review for security vulnerabilities`
- Codex cloud with PR `.diff`
- Codex CLI/IDE if connected to the repo

## Authority
Cody can approve, request revision, or block.
Cody cannot merge.
Cody cannot override Security Reviewer, System Architect, or Senior QA.
