---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - tools-and-interfaces
---

# Safe Exact-Anchor Editing

## Core idea and problem
Whole-file writes from stale snapshots silently clobber concurrent changes.

## How it works
edit(path, oldText, newText, mode): authorize, resolve safe path, verify exact unique current anchor, preview, atomic replace. Denied vs conflict vs failed vs ok receipts.

## Example / failure mode
Two calls read same file; later write erases earlier change.

## Implementation and verification notes
Atomic rename prevents partial bytes, not stale semantics. Serialize local mutations; multi-process needs shared lock/version.

## Connected concepts
- [Authority Policy](../03%20-%20Power/Authority%20Policy.md)
- [Harness-Control Tests](../10%20-%20Harness%20Testing/Harness-Control%20Tests.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?
