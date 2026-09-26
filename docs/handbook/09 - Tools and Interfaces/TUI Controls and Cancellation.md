---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - tools-and-interfaces
---

# TUI Controls and Cancellation

## Core idea and problem
Human slash commands can be misread as model tasks; forceful termination can interrupt side effects.

## How it works
Separate /help, /status, /context, /new, /cancel, /exit from plain tasks; // escape. UI watches events; kernel owns state. Cancel via abort, await cleanup, record outcome.

## Example / failure mode
/status forwarded to model, which tries to implement status feature.

## Implementation and verification notes
During active run allow safe status/help/cancel; refuse new/policy/context changes as BUSY if necessary.

## Connected concepts
- [Agent Loop and Provider Seam](../08%20-%20Agent%20Runtime/Agent%20Loop%20and%20Provider%20Seam.md)
- [Append-Only Journal](../07%20-%20Carry/Append-Only%20Journal.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

A cancellation acknowledgment does not undo effects already committed. See [Budgets and Termination](../08%20-%20Agent%20Runtime/Budgets%20and%20Termination.md) for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [Source Coverage Index](../00%20-%20Start%20Here/Source%20Coverage%20Index.md).
