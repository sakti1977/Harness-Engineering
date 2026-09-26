---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - verdict
---

# Verification Routes and Test Fidelity

## Core idea and problem
A run proves only the path it exercised. Sequential and mocked tests can miss production races.

## How it works
Route fields Claim, Entry, Boundaries, Setup, Actions, Observations, Cleanup. Check entry/state/timing/response/persistence fidelity. Create concurrent requests before awaiting; inspect responses and shared DB.

## Example / failure mode
Two booking requests both read free then both insert, returning 201 twice.

## Implementation and verification notes
A faithful red E2E test is a successful harness detection; keep feature active.

## Connected concepts
- [[Claim-to-Proof Matrix]]
- [[Readiness Contract]]
- [[First Divergence and Failure Packet]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Run a helper check and persistent-state checks on the same broken implementation to see the proof gap. See [[First Executable Harness Lab]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
