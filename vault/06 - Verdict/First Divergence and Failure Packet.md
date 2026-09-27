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
- [[Append-Only Journal]]
- [[Claim-to-Proof Matrix]]
- [[Secret Handling]]

## Practical extension

Turn the minimal reproduction into a regression case before closing the incident. See [[Failure to Evaluation Workflow]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
