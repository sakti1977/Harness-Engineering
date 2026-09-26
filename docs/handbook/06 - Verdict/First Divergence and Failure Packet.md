---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - verdict
---

# First Divergence and Failure Packet

## Core idea and problem
Later failures distract from the first actual departure from expected execution.

## How it works
Trace action/runtime/decision with run/turn/feature/tool IDs, sequence, revision, permit, result, evidence. Failure packet: expected, actual, first divergent event, affected claim, reproduction, next boundary.

## Example / failure mode
waitlist.mark_promoted affects zero rows; later notification failure is downstream.

## Implementation and verification notes
Record applied rules and observations, not hidden reasoning; redact secrets and patient data.

## Connected concepts
- [Append-Only Journal](../07%20-%20Carry/Append-Only%20Journal.md)
- [Claim-to-Proof Matrix](Claim-to-Proof%20Matrix.md)
- [Secret Handling](../03%20-%20Power/Secret%20Handling.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Turn the minimal reproduction into a regression case before closing the incident. See [Failure to Evaluation Workflow](../10%20-%20Harness%20Testing/Failure%20to%20Evaluation%20Workflow.md) for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [Source Coverage Index](../00%20-%20Start%20Here/Source%20Coverage%20Index.md).
