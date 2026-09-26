---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - carry
---

# Cold-Session Checkpoint

## Core idea and problem
“Mostly implemented” loses diagnosis and invites the next session to repeat or contradict work.

## How it works
Record active outcome, revision/dirty state, commands/results, expected vs actual, preserved decisions, non-obvious diagnosis, first reproduction command, next bounded edit. Reconcile with actual repo on resume.

## Example / failure mode
Session discovers booking transaction bug but next agent only sees vague handoff.

## Implementation and verification notes
Prefer “both requests returned 201 and two rows persisted” over “almost done”.

## Connected concepts
- [[Append-Only Journal]]
- [[Resume Replay and Fork]]
- [[Recovery Audit]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Check stored revision and unresolved effects against current state before acting. See [[Memory Scope and Retention]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
