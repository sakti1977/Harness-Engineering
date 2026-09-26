---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - scope
---

# Scope Contract

## Core idea and problem
Agent drifts from atomic change into refactors and renames.

## How it works
Define Outcome, Expected surface, Exclusions, Evidence, Discovery rule. Execute inside scope; Amend necessary dependency; Queue interesting work; Block only for external permission/decision/dependency.

## Example / failure mode
Atomic cancel-and-replace ticket expands into 11 changed files while core flow remains broken.

## Implementation and verification notes
Completion = verified outcome + final diff reconciled with scope + queued discoveries left undone. File count is not a quality metric.

## Connected concepts
- [Feature Ledger as a Gate](../06%20-%20Verdict/Feature%20Ledger%20as%20a%20Gate.md)
- [Claim-to-Proof Matrix](../06%20-%20Verdict/Claim-to-Proof%20Matrix.md)
- [Authority Policy](../03%20-%20Power/Authority%20Policy.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?
