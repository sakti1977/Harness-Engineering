---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - ground
---

# Readiness Contract

## Core idea and problem
Tests against unusable setup produce meaningless green results.

## How it works
Contract: Claim, Probe, Pass evidence, Recovery. Check runtime, config, seed data, service boundary, baseline verification. Report PASS/FAIL/SKIP; READY only when required probes pass.

## Example / failure mode
A booking test passes against empty DB and never exercises collision.

## Implementation and verification notes
Dependent probes SKIP on failed prerequisites; blocked exits nonzero.

## Connected concepts
- [[Initialization Session]]
- [[Claim-to-Proof Matrix]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Record the environment actually exercised; artifact existence is weaker than a readiness probe. See [[Reproducible Evaluation Environment]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
