---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - carry
---

# Resume Replay and Fork

## Core idea and problem
Continuing, inspecting, and branching execution are not interchangeable.

## How it works
Replay reads history without provider/tools/writes. Resume appends new work after settled history. Fork makes independent child from settled state; parent unchanged. Unresolved tool calls block resume/fork.

## Example / failure mode
A saved edit call has no result; do not rerun it merely because the journal lacks receipt.

## Implementation and verification notes
Fork copies safe parent history plus provenance; refuse existing child collision.

## Connected concepts
- [Append-Only Journal](Append-Only%20Journal.md)
- [Cold-Session Checkpoint](Cold-Session%20Checkpoint.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Reconcile ambiguous external effects before retrying a resumed action. See [Retry and Idempotency Contract](../08%20-%20Agent%20Runtime/Retry%20and%20Idempotency%20Contract.md) for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [Source Coverage Index](../00%20-%20Start%20Here/Source%20Coverage%20Index.md).
