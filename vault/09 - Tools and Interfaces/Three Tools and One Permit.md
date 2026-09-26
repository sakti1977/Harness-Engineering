---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - tools-and-interfaces
---

# Three Tools and One Permit

## Core idea and problem
Tool availability is not authorization.

## How it works
Start with read, write/edit, bash; every request passes one permit. Reject unknown tools, path escape, secret read, unauthorized writes, disallowed commands. Use argv-based execution rather than unrestricted shell.

## Example / failure mode
Provider advertises bash, but agent requests db:reset on shared DB; permit refuses.

## Implementation and verification notes
Bound read/output/time; denial is normal observable result, distinct from runtime failure.

## Connected concepts
- [[Authority Policy]]
- [[Tool Extension Contract]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Validate structure, domain meaning and authorization separately. See [[Typed Outputs and Semantic Validation]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
