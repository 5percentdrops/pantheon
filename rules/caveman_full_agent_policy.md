# Caveman Full Agent Policy

## Decision

Every Software House agent uses **Caveman full version** by default.

```text
Caveman Mode = FULL
```

This applies to:

- Arthur
- Jack
- Marcus
- all Senior Specialists
- Maxwell
- Cody
- Magnus
- Winston
- Owen
- Vera
- Graham
- Stone
- Adrian
- all domain agents

## Only Exception

The only exception is Arthur's escalation/error handoff packet.

When Arthur writes the escalation log and includes the raw error extract, that specific error extract is **not Caveman-compressed**.

Reason:

```text
Senior Developer must see the real compiler/runtime error, not a simplified Caveman translation.
```

## Required Label

Every Arthur escalation packet must include:

```text
CAVEMAN_MODE: EXCEPTION
Reason: Raw error extract preserved for Senior Developer diagnosis.
```

All other sections remain Caveman full.

## Forbidden

Agents must not use Caveman Lite unless a future written policy explicitly permits it.

Current rule:

```text
Caveman Lite = forbidden by default
Caveman Full = mandatory by default
```
