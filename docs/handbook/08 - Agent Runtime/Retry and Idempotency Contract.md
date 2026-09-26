---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Retry and Idempotency Contract

## Problem

A request may succeed even when its response is lost. Blindly retrying a write can duplicate its effect.

## Mechanism

Classify failures as retryable, permanent or outcome-unknown. Bound attempts and total elapsed time; use backoff with jitter for retryable failures. Give a logical write a stable idempotency key and bind that key to its intended payload. Reconcile outcome-unknown operations before retrying with a new identity.

## Worked example

A booking service commits an appointment and the connection closes before the response arrives. The client queries the original request identity or retries with the same identity. Reusing that identity for a different appointment must fail.

## Try it and check the result

In a mock service, crash after saving the effect but before returning its receipt. Resume with the same key and assert one stored effect. Try the same key with a different payload and expect a conflict. Test expiry and late-arriving requests separately.

## Tradeoffs and limits

An idempotency key works only if the receiver enforces the contract and retains it long enough. It cannot guarantee exactly-once behavior across arbitrary services. Permanent authorization failures should not be retried as transient errors.

## Sources and interpretation

[AWS: making retries safe](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) explains ambiguous effects and request identities. [AWS: backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) covers retry timing.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Append-Only Journal](../07%20-%20Carry/Append-Only%20Journal.md)
- [Resume Replay and Fork](../07%20-%20Carry/Resume%20Replay%20and%20Fork.md)
- [Budgets and Termination](Budgets%20and%20Termination.md)
