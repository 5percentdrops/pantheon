# Lane Concurrency Policy

Only two engineering lanes may be active at once.

If two lanes are active and a third is requested, Arthur must queue the third lane.

This protects Mac Mini 16GB RAM and SQLite project memory.
