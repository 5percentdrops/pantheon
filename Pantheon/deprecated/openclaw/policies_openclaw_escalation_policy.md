# OpenClaw Escalation Policy

OpenClaw executes procedural work.

Escalate to Hermes when:
1. The task requires judgment rather than procedure.
2. Required input is missing and cannot be inferred safely.
3. The next route is ambiguous.
4. A security, compliance, financial, deployment, or platform-risk issue appears.
5. Output quality fails acceptance criteria.
6. A tool error repeats after the allowed retry count.
7. A decision could affect architecture, security, money, production, or build quality.
8. The same failure repeats and may require a new Hermes skill.

When escalating:
- Stop execution.
- Preserve all inputs/logs.
- Create an escalation packet.
- Send it to the mapped Hermes agent.
- Mark the task blocked until Hermes returns a decision.
