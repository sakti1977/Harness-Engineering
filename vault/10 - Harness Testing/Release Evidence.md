---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - harness-testing
---

# Release Evidence

## Core idea and problem
Green developer tests do not necessarily describe the shipped archive.

## How it works
Evidence travels with artifact: Snapshot, Command, Location, Result. Check required files before running; execute against release snapshot; preserve receipt. Later add hash, clean unpack, full logs.

## Example / failure mode
Tarball omits tests that were present on developer machine.

## Implementation and verification notes
Record exact argv/cwd/exit and revision; verify packaged thing, not a nearby workspace.

## Connected concepts
- [[Claim-to-Proof Matrix]]
- [[Readiness Contract]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Tie evidence to the task, patch, harness and environment versions actually exercised. See [[Reproducible Evaluation Environment]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
