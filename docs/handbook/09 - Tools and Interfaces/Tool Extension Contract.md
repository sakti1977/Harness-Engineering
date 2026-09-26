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
- [Three Tools and One Permit](Three%20Tools%20and%20One%20Permit.md)
- [Harness-Control Tests](../10%20-%20Harness%20Testing/Harness-Control%20Tests.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Contract correctness and agent usability need different tests. See [Tool Usability Evaluations](Tool%20Usability%20Evaluations.md) for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [Source Coverage Index](../00%20-%20Start%20Here/Source%20Coverage%20Index.md).
