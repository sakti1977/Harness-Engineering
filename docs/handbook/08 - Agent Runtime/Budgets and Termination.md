---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Budgets and Termination

## Problem

A loop that stops only when the model says done can spend indefinitely or end without enough time to verify its work.

## Mechanism

Track steps, elapsed time and estimated/reported cost. Reserve a verification allowance. Distinguish completed, blocked, cancelled, budget-exhausted and infrastructure-failed. Preserve a checkpoint before exiting. Treat repeated identical failures as a signal to reconsider the approach, not as proof that one more retry will work.

## Worked example

A model call begins just below the spending limit and pushes usage above it. A pre-call threshold is a soft limit unless the maximum next-call charge is reserved or capped by the provider.

## Try it and check the result

Script a loop that repeats one failing action. Confirm its stop reason and checkpoint after the attempt limit. Inject cancellation while a write is in flight and report whether the external effect is known, absent or still uncertain.

## Tradeoffs and limits

Loop detectors can stop legitimate iterative work. Evaluate false stops and recovered tasks. Cancellation acknowledgment is not rollback of an already completed operation.

## Sources and interpretation

[mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) has a readable bounded loop; [Codex: app-server protocol](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md) documents cancellation semantics. Threshold choices here require workload testing.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Agent Loop and Provider Seam](Agent%20Loop%20and%20Provider%20Seam.md)
- [Retry and Idempotency Contract](Retry%20and%20Idempotency%20Contract.md)
- [TUI Controls and Cancellation](../09%20-%20Tools%20and%20Interfaces/TUI%20Controls%20and%20Cancellation.md)
