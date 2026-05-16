# SoftwareHouse Review Report

## Verdict

The original Software House concept is strong. It already has:
- clear Brain/Hands pattern,
- human names,
- good desk structure,
- Project Manager as single user-facing contact,
- Senior Advisor → Executor escalation loop,
- QA and functional testing,
- specialised trading indicator/data/backtesting desks,
- Hermes learning-loop mindset.

## Changes made

| Area | Change |
|---|---|
| Architecture | Added Priya — System Architect. This enforces architecture review before implementation and reduces cross-desk contract drift. |
| Security | Added Safiya — Security Reviewer. This is essential for trading systems, API keys, OAuth, Supabase, execution paths, and deployment safety. |
| Harness split | Converted purely procedural agents to OpenClaw: Backtester, DevOps Developer, Functional Tester, Indicator Tester. |
| Seed skills | Added Hermes seed skills and OpenClaw procedural seed skills for every agent. |
| Escalation | Added explicit OpenClaw → Hermes escalation rules. |
| Install structure | Converted to standalone plug-and-play CoreSeed-style package. |

## Main challenge

The original repo was too API/onboarding-prompt oriented and not aligned with the final CoreSeed boundary. This version keeps Paperclip as the organisation registry, gives Hermes and OpenClaw starting skills, but does not try to control either harness internally.

## Final agent count

23 agents:
- 21 original agents
- Priya — System Architect
- Safiya — Security Reviewer
