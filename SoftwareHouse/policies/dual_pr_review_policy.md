# Dual PR Review Policy

## Rule
Every implementation pull request must pass two PR review gates before merge readiness:

1. Clara — Claude PR Review Lead
   - Harness: Hermes
   - Underlying engine: Claude Code Review / Opus 4.7
   - Role: first-line deep review

2. Cody — Hermes Codex PR Reviewer
   - Harness: Hermes
   - Underlying engine: latest Codex coding/review model
   - Role: second-line review, runnable-fix/test/security/codebase pass

## Specialist escalation
After Clara and Cody, route conditionally:

- Security/auth/API keys/OAuth/Supabase/trading execution/payments/database/infra → Safiya
- Architecture/service boundaries/data flow/module design → Priya
- Tests/coverage/CI/acceptance criteria → Nadia
- Requirement ambiguity/merge readiness → Arthur

## Learning
Hermes must learn from both reviewers:
- repeated defects
- repeated missing tests
- successful fix patterns
- recurring architecture drift
- recurring security patterns
- new code patterns requiring review heuristics
