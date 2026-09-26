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
- [Authority Policy](../03%20-%20Power/Authority%20Policy.md)
- [Feature Ledger as a Gate](../06%20-%20Verdict/Feature%20Ledger%20as%20a%20Gate.md)
- [Safe Exact-Anchor Editing](../09%20-%20Tools%20and%20Interfaces/Safe%20Exact-Anchor%20Editing.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Keep deterministic control fixtures separate from stochastic live-agent trials. See [Agent Evaluation Suite](Agent%20Evaluation%20Suite.md) for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [Source Coverage Index](../00%20-%20Start%20Here/Source%20Coverage%20Index.md).
