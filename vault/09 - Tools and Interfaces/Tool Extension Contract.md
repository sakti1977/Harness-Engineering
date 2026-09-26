---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - tools-and-interfaces
---

# Tool Extension Contract

## Core idea and problem
Provider schema, permit, runner, and tests drift when a tool is added ad hoc.

## How it works
One capability contract: name, description, input schema, permit, runner, lock, receipt, drift tests. Schema ≠ permission; permission ≠ successful verdict.

## Example / failure mode
test tool is advertised but executor or allowlist does not recognize it.

## Implementation and verification notes
Add clean/denied/failure/cancel fixtures; event ownership remains kernel-side.

## Connected concepts
- [[Three Tools and One Permit]]
- [[Harness-Control Tests]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Contract correctness and agent usability need different tests. See [[Tool Usability Evaluations]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
