---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - harness-testing
---

# Harness-Control Tests

## Core idea and problem
A green gate may mean it works—or that it never inspected the defect.

## How it works
Use deterministic seeded repo + scripted agent request. Test control, not live model. Pair defect fixture and clean fixture. Mutation-test unconditional allow and unconditional deny.

## Example / failure mode
Scope gate printed OK because it checked wrong git diff surface.

## Implementation and verification notes
Codes: PATH_OUTSIDE_SURFACE, SECRET_PATH_DENIED, INVALID_TRANSITION, STALE_EVIDENCE, CLAIM_UNCOVERED. Rejected writes leave state unchanged.

## Connected concepts
- [[Authority Policy]]
- [[Feature Ledger as a Gate]]
- [[Safe Exact-Anchor Editing]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Keep deterministic control fixtures separate from stochastic live-agent trials. See [[Agent Evaluation Suite]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
