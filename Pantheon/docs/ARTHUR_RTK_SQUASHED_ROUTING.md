# Arthur RTK-Squashed Routing

## Rule
Arthur must not forward full logs or full escalation history to Jack or any standard developer.

## Maximum handoff
3 lines.

## Format

```txt
1. Problem: <one-line blocker summary>
2. Action: <exact next instruction>
3. Reference: <path to full log/report/template>
```

## Hard rules
- No full log dumps in routing messages.
- No full blocker histories in routing messages.
- Pass references to `wiki/errors/`, reports, and packets instead.
- Full logs remain in Obsidian/wiki files.
