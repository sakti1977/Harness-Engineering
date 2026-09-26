---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - practical-implementations
---

# Minimal Harness Adoption Path

## Core idea and problem
Overbuilding a harness before observing failures creates maintenance burden.

## How it works
Start with one observable outcome, scope, real proof route, restricted execution, receipts. Add ledger for multiple features, journal for long runs, compaction for context, safe edit for concurrency, release gate for shipping.

## Example / failure mode
Start by proving clinic double-booking, not by implementing a full agent framework.

## Implementation and verification notes
Observed failure → smallest fixture → owning control → cost measurement → retest after model change.

## Connected concepts
- [[Five Layers of a Harness]]
- [[Harness-Control Tests]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Start with one observed failure, then run the model-free booking lab before expanding controls. See [[Project Harness Assessment]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
