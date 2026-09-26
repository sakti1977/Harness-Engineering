---
type: moc
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - carry
---

# Carry - MOC

## Core idea and problem
What survives a session and makes continuation safe?

## How it works
Study these concepts in relation, not as independent tips.

## Example / failure mode
A missing layer can invalidate an otherwise plausible agent result.

## Implementation and verification notes
Return to [Harness Engineering - MOC](../00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md).

## Connected concepts
- [Cold-Session Checkpoint](Cold-Session%20Checkpoint.md)
- [Append-Only Journal](Append-Only%20Journal.md)
- [Context Compaction Contract](Context%20Compaction%20Contract.md)
- [Resume Replay and Fork](Resume%20Replay%20and%20Fork.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Further study

- [Memory Scope and Retention](Memory%20Scope%20and%20Retention.md)
