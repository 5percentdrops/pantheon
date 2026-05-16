# RTK Error Extract Policy

## Role

RTK is terminal/output compression only.

```text
RTK is not a harness.
Hermes remains the only harness.
```

## Required Error Extraction

For failed execution escalation, RTK must preserve:

```text
HEAD = first 150 lines of final error
TAIL = last 150 lines of final error
MIDDLE = stripped
```

This is the 150/150 rule.

## If Error Is Shorter Than 300 Lines

If the full error is fewer than 300 lines, preserve the complete error.

## If Error Is Missing

If the final error cannot be extracted, Arthur must still send the escalation packet to the assigned Senior Developer with:

```text
ERROR_EXTRACT_STATUS: MISSING
Action: Senior Developer must inspect repo/tests/logs directly.
```

## If Error Is Partial

If only part of the error is available, Arthur must send the partial error and include:

```text
ERROR_EXTRACT_STATUS: PARTIAL
Action: Senior Developer must inspect repo/tests/logs directly.
```

## Forbidden

RTK must not rewrite the semantic meaning of errors.

RTK may:

- remove repeated noise
- strip middle logs
- preserve head/tail
- preserve exact compiler/runtime messages

RTK must not:

- summarize away the real error
- hallucinate missing lines
- modify code
- act as a harness
