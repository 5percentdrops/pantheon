# User Approval Gate

## Delivery
After the PRD passes advisory review, Arthur delivers it to the user via Discord or Telegram.

## User response

### If user requests revision
```txt
User revision
→ Arthur
→ restart pipeline from beginning
```

### If user approves
```txt
User approval
→ Arthur
→ Marcus
→ SDD
→ feature tickets
→ task-level TDD
→ Jack execution
```

## Hard rules
- Arthur cannot kill the project without explicit user instruction.
- Arthur cannot override user approval.
- User approval is final unless the user later revises or cancels.
