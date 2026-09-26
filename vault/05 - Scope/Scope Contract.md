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
- [[Feature Ledger as a Gate]]
- [[Claim-to-Proof Matrix]]
- [[Authority Policy]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?
