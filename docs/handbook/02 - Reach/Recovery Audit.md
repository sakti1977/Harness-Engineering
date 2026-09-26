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
Observe what it reads *before* editing; repair navigation rather than only adding prompt length.

## Connected concepts
- [Repository as Shared Context](Repository%20as%20Shared%20Context.md)
- [Cold-Session Checkpoint](../07%20-%20Carry/Cold-Session%20Checkpoint.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?
