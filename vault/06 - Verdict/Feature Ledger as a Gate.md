---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - verdict
---

# Feature Ledger as a Gate

## Core idea and problem
A feature list that agents can self-mark passing becomes a false memory for later sessions.

## How it works
Ledger fields id, behavior, state, depends_on, verification, evidence, blocked_on. Planner owns plan; worker requests; verifier owns verdict; invalidator revokes stale proof. Reject unauthorized transitions atomically.

## Example / failure mode
CLIN-511 marked passing although E2E failed; next session trusts it.

## Implementation and verification notes
Test no-evidence passing, duplicate IDs, missing dependencies, unauthorized planner edits, stale revision; rejected ledger remains byte-identical.

## Connected concepts
- [[Claim-to-Proof Matrix]]
- [[Scope Contract]]
- [[Harness-Control Tests]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

The starter validator accepts planned, active, blocked and ready_for_verification. It deliberately rejects self-attested passing; it does not yet implement an independently evidenced completion transition. See [[Project Harness Assessment]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
