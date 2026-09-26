---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - carry
---

# Context Compaction Contract

## Core idea and problem
Naively dropping old messages can separate calls/results and erase permission receipts.

## How it works
Desk vs filing cabinet: model context is desk; journal is durable filing cabinet. Meter, Budget, Retention, Receipt. Keep policy and latest complete exchange; compact older settled material with visible partial receipt.

## Example / failure mode
12 turns exhaust context; naive summary invents a decision and loses earlier tool denial.

## Implementation and verification notes
Never compact unresolved tool call; block if newest complete exchange cannot fit.

## Connected concepts
- [Append-Only Journal](Append-Only%20Journal.md)
- [Agent Loop and Provider Seam](../08%20-%20Agent%20Runtime/Agent%20Loop%20and%20Provider%20Seam.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Worked cold-resume exercise

Before compaction, suppose the journal contains: task BOOK-1; a denied production write; an approved disposable SQLite fixture; a failed concurrency assertion; and an unresolved tool request. A valid checkpoint retains those distinctions and the current revision. It must not turn “proposed transaction fix” into “verified fix.”

A compact handoff can say: “BOOK-1 remains active. Production writes are denied. The local concurrency check produced two rows. No fix is verified. Reconcile outstanding request tool-17 before resuming. Read the saved trace and rerun the reviewed local test.”

Give only the checkpoint and referenced artifacts to a fresh session. Ask it to identify authority, failure, uncertain effects and next action. Compare its answers to the original journal. This is an exercise specification, not a completed model experiment.

[Anthropic’s context engineering article](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) discusses compaction and durable notes. This worked checkpoint is local synthesis. See [Memory Scope and Retention](Memory%20Scope%20and%20Retention.md).
