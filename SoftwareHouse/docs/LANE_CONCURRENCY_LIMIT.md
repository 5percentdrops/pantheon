# Lane Concurrency Limit

## Rule
Only two engineering lanes may be active at the same time.

## Reason
Mac Mini 16GB RAM may struggle when multiple SQLite project memory contexts are open.

## Heavy lane warning
Do not run Backend, TradingView/Pine Script, and Quantower/C# all at once.

## Arthur duty
Arthur must maintain:
- active lanes
- queued lanes
- paused lanes
- completed lanes

If a third lane is requested, Arthur queues it until one active lane is paused, completed, or closed.
