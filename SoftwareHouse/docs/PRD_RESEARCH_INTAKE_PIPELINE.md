# PRD Research / Intake Pipeline

## Purpose
This pipeline happens before engineering.

It prevents the Software House from building from a weak PRD, wrong route, bad API, stale library, or unqualified assumption.

## Flow

```txt
Raw Idea
→ Owen — Research Pack Agent
→ Vera — API & Bottleneck Intelligence Agent
→ Graham — Feasibility Strategist
→ Stone — Skeptical Validation Agent
→ Graham revision loop if needed
→ Adrian — Opportunity Architect
→ Arthur — User Approval Gate
→ User approves or requests revision
→ Arthur routes approved PRD to relevant senior owner by technical domain
→ Engineering pipeline starts
```

## Critical rule
Approved PRDs do not default to Marcus.

Arthur routes by technical domain:
- Backend/API/service → Marcus
- Frontend/web → Sonia
- Mobile → Dominic
- TradingView/Pine Script → Felix
- Quantower/C# → Nathan
- DevOps/infra → Viktor
- QA/test architecture → Nadia
