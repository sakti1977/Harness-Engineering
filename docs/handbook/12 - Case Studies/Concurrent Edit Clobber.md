---
type: case-study
evidence_kind: instructional-scenario
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - case-studies
---

# Concurrent Edit Clobber

> **Evidence status:** an instructional scenario inherited from earlier shared material. No independently verified production incident is claimed.

## Core idea and problem
Two calls use stale same-file snapshots.

## How it works
Exact-anchor conflict detection and serialized mutations.

## Example / failure mode
Later whole-file write erases earlier valid change.

## Connected concepts
- [Safe Exact-Anchor Editing](../09%20-%20Tools%20and%20Interfaces/Safe%20Exact-Anchor%20Editing.md)
- [Harness-Control Tests](../10%20-%20Harness%20Testing/Harness-Control%20Tests.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Reproduction route

Use [Case Study Template](../Templates/Case%20Study%20Template.md) to record evidence and uncertainty. The scenario does not yet have an executed local reproduction; see [Failure to Evaluation Workflow](../10%20-%20Harness%20Testing/Failure%20to%20Evaluation%20Workflow.md).
