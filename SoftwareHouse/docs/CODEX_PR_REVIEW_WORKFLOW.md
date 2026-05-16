# Hermes Codex PR Review Workflow

## Goal
Codex is added as the code-review engine, but Hermes is the harness so Cody learns over time.

## Flow
1. Implementation agent completes ticket.
2. PR is opened/submitted.
3. Cody — Hermes Codex PR Reviewer reviews the PR.
4. Cody asks Codex to inspect the diff.
5. Cody compares:
   - diff
   - ticket
   - PRD
   - SDD
   - tests
   - CI logs
   - repo rules
   - prior Hermes review memories
6. Cody outputs approve / revise / block.
7. Cody creates Hermes learning candidates from recurring issues or successful fixes.
8. Findings route back to the correct specialist.
9. Clean PRs move to merge readiness.

## Important
Codex is not the harness.
Hermes is the harness.
Codex is the underlying code-review engine.
Arthur remains the project-manager contact.
Safiya can override on security.
Priya can override on architecture.
Nadia can block on QA/test coverage.
