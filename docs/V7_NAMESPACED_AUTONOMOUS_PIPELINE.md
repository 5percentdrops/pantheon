> V8.1 note: canonical Arthur model is `openai/gpt-5-mini` under Hermes. Older Watcher/Core or DeepSeek/Opus Arthur claims are deprecated.

# Pantheon V7.0 — Namespaced Autonomous Pipeline

**Version:** 7.0  
**Architecture:** Global namespaced workspace  
**Budget target:** $6.66/day API strict cap  
**Harness rule:** Hermes only  
**RTK rule:** RTK is terminal/output compression only, never a harness.

## 1. Core Decision

Pantheon keeps the large org-chart, but operates with a smaller active squad by default.

Default active squad:

| Role | Agent | Model class | Purpose |
|---|---|---|---|
 | Manager / Router | Arthur model: GPT-5 mini under Hermes | Cheap reasoning model | State control, routing, namespace safety | 
| Standard Dev | Jack | DeepSeek V4 Pro | Implements ticket + red test |
| Senior Specialist | Domain Senior | Opus-class model when needed | SDD, tickets, red tests, final commit |
| Auditor | Cody | GPT/Codex reviewer | Independent code audit |
| Archivist | Winston | Cheap reliable summarizer | Archives final artifacts and error memory |

Dormant specialists wake only when required.

## 2. Namespaced Directory Architecture

Every project artifact is keyed by `[Project_Title]`.

```text
Global_Workspace/
├── 01_PRDs/
│   └── [Project_Title]_PRD.md
├── 02_SDDs/
│   └── [Project_Title]_SDD.md
├── 03_Feature_Tickets/
│   └── [Project_Title]/
│       └── [Ticket_ID]_[Ticket_Name].md
├── 04_TDD_Red_Tests/
│   └── [Project_Title]/
│       └── [Ticket_ID]_[Test_Name].rs
├── 05_QA_Audit_Logs/
│   └── [Project_Title]/
│       ├── [Project_Title]_Escalation_Log.md
│       ├── [Project_Title]_Forensic_Report.md
│       ├── [Ticket_ID]_Pass.md
│       └── [Ticket_ID]_Fail.md
├── 06_Project_Repos/
│   └── [Project_Title]/
│       ├── src/
│       ├── tests/
│       ├── Cargo.toml
│       └── README.md
├── 07_Finalization/
│   └── [Project_Title]/
│       ├── [Ticket_ID]_Commit_Readiness.md
│       ├── [Ticket_ID]_PR_Description.md
│       └── [Ticket_ID]_Merge_Checklist.md
└── MASTER_STATUS.md
```

## 3. Arthur Model Policy

```text
Arthur model = openai/gpt-5-mini under Hermes
```

Arthur is a single-model manager/router/state-controller. If confidence is low, Arthur routes to the assigned Senior or the user instead of guessing. The historical Watcher/Core split is deprecated; see `Pantheon/deprecated/` for the archived design.

## 4. Retry Ladder

The old 21-attempt junior loop is replaced.

| Stage | Attempts | Owner |
|---|---:|---|
| Junior implementation | 1–12 | Jack / DeepSeek V4 Pro |
| Senior tactical fix | 13–15 | Assigned Senior |
| Maxwell deep fix | 16–17 | Opus Max effort |
| Cody forensic audit | 18 | Codex/GPT reviewer |
| Magnus architecture rethink | 19 | Principal architect |

Rule:

```text
If Junior cannot fix it in 12 attempts, the problem is no longer treated as a Junior problem.
```

## 5. Success Path

```text
PRD → SDD → Tickets + Red Tests → Junior Green → Cody Pass → Senior Final Review → Commit → PR → MASTER_STATUS update → Winston Archive → Merge Gate
```

## 6. Commit and Merge Authority

| Action | Owner |
|---|---|
| Implement code | Junior |
| Run tests | Junior |
| Audit implementation | Cody |
| Final architecture sanity check | Senior |
| Commit to feature branch | Senior |
| Push branch | Senior |
| Draft PR | Senior |
| Merge to main | User-gated or Arthur-gated only |
| Archive final memory | Winston |

Junior must not finalize project history.

## 7. Winston Memory Rule

Winston archives final artifacts and real lessons only. Winston does not archive every retry.

Archive: PRD, SDD, completed feature ticket, red test, pass log, commit readiness packet, PR description, worked solution, failed solution worth remembering, prevention rule.

Do not archive: full terminal spam, every retry, temporary chain notes, low-value syntax noise.

## Caveman Full Requirement

Every agent uses Caveman full version by default.

```text
Caveman Mode = FULL
```

Only exception:

```text
Arthur's raw escalation error extract = CAVEMAN_MODE: EXCEPTION
```

The raw error extract must not be Caveman-compressed because the assigned Senior Developer needs the real compiler/runtime failure.

## Arthur Senior Handoff Requirement

When Junior fails the capped retry loop, Arthur must:

1. Write a sub-50-line failure summary.
2. Preserve RTK final error extract using 150 head lines and 150 tail lines.
3. Mark missing/partial errors clearly.
4. Hand the escalation packet to the assigned Senior Developer.
5. Send available error material even if something is missing.



## Arthur as Head / Project Manager

Arthur is the first role set up in the Paperclip-style organisation.

Paperclip may call this top role the CEO, but this repo renames it:

```text
Arthur = Project Manager / Head
```

Arthur is responsible for hiring or activating any additional specialist agents if the default team needs them.

Arthur must not silently expand the team.  
If a specialist is needed, Arthur writes a hiring packet and records the explicit project requirement.

## Full Pantheon Specialist Activation

The full Pantheon may include frontend, mobile, Pine Script, Quantower/C#, DevOps, QA, and research specialists.

They are not automatically active on every project.

Default rule:

```text
Use the smallest safe team first.
Arthur activates specialists only when needed.
```
