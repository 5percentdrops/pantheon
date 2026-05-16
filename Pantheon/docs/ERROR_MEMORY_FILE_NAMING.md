# Error Memory File Naming

All files in `wiki/errors/` must use one of these patterns:

```txt
YYYY-MM-DD_<slug>__BLOCKER_LOG.md
YYYY-MM-DD_<slug>__SOLUTION_LOG.md
YYYY-MM-DD_<slug>__CODE_FIX_LOG.md
YYYY-MM-DD_<slug>__APPROACH_SOLUTION_LOG.md
```

Examples:

```txt
2026-05-02_youtube-transcript-rate-limit__BLOCKER_LOG.md
2026-05-02_youtube-transcript-rate-limit__SOLUTION_LOG.md
2026-05-02_youtube-transcript-rate-limit__APPROACH_SOLUTION_LOG.md
```

## Slug rule
Use a short, searchable slug based on the error:

```txt
youtube-transcript-rate-limit
quantower-csharp-order-event-null
pinescript-repaint-alert-bug
supabase-rls-policy-denied
```
