---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - verdict
---

# Claim-to-Proof Matrix

## Core idea and problem
A helper test may pass while the real route never invokes the helper.

## How it works
Map each acceptance claim to observation, evidence producer, and gap. Outcome evidence supports claim; diagnostic evidence explains; contradiction vetoes passing. Require current proof for all claims.

## Example / failure mode
Conflicting booking returns 409 AND persists no row; unit-only validator test cannot establish either at HTTP+DB boundary.

## Implementation and verification notes
Changing claim, observation, producer, route, or revision invalidates affected verdict. Worker submits evidence, not terminal state.

## Connected concepts
- [[Verification Routes and Test Fidelity]]
- [[Feature Ledger as a Gate]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Verify that a grader rejects a plausible broken solution and accepts a valid alternative. See [[Grader Reliability]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
