---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - carry
---

# Append-Only Journal

## Core idea and problem
Process death can lose tool results and make a write uncertain.

## How it works
Append-only JSONL source of truth; derive messages. Await event persistence. Recover complete lines before torn tail. Match tool calls to results; unresolved call means uncertain side effect.

## Example / failure mode
Process exits after edit request but before receipt; blindly retrying may duplicate mutation.

## Implementation and verification notes
Events: run_start, assistant_message, tool_call, tool_result, turn_end, compact, run_end. Snapshot is an inspection aid, not substitute.

## Connected concepts
- [[Resume Replay and Fork]]
- [[Context Compaction Contract]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

A recorded attempt is not proof that its effect occurred exactly once. See [[Retry and Idempotency Contract]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
