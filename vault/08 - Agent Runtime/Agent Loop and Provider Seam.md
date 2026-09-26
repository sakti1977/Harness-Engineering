---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - agent-runtime
---

# Agent Loop and Provider Seam

## Core idea and problem
A coding agent needs a bounded loop that records model replies and tool results.

## How it works
Send conversation → reply → authorize and execute tools → append results → repeat until stop/budget/cancel. Provider seam hides model format; ScriptedProvider enables deterministic tests. Events are observational.

## Example / failure mode
Truncated provider reply includes partial tool batch: do not execute it.

## Implementation and verification notes
Assistant message before tool calls; ordered calls; awaited journal; run_end for errors/cancel; turn budget.

## Connected concepts
- [[Three Tools and One Permit]]
- [[Append-Only Journal]]
- [[TUI Controls and Cancellation]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Record an explicit stop reason and preserve verification time. See [[Budgets and Termination]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
