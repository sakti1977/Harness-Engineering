---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - reach
---

# Recovery Audit

## Core idea and problem
A fresh session may not recover the correct route to a task.

## How it works
Audit Root (entry), Route (owner), Check (verification), Remove (stale guidance). Ask a cold agent to find owner, run setup, locate invariant, and reproduce test.

## Example / failure mode
A new session guesses an endpoint while the canonical booking rule is elsewhere.

## Implementation and verification notes

Run it against the handoff: in a session with no history, `python3 scripts/harness_handoff.py --resume` must answer eight questions with a file or command for each before any edit. Then change the repository after writing the checkpoint and confirm it reports `CHECKPOINT_STALE`.

Observe what it reads *before* editing; repair navigation rather than only adding prompt length.

## Connected concepts
- [[Repository as Shared Context]]
- [[Cold-Session Checkpoint]]
