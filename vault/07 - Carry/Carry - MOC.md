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
Return to [[Harness Engineering - MOC]].

## Connected concepts
- [[Cold-Session Checkpoint]]
- [[Append-Only Journal]]
- [[Context Compaction Contract]]
- [[Resume Replay and Fork]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Further study

- [[Memory Scope and Retention]]
