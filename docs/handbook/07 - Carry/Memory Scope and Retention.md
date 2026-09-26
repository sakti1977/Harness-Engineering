---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Memory Scope and Retention

## Problem

A checkpoint, a transcript and a cross-project memory store serve different purposes. Mixing them can leak data or preserve stale instructions.

## Mechanism

Use run-local state for active actions, thread checkpoints for resumption, and explicitly scoped durable knowledge for facts intended to outlive the task. Store origin, owner, revision and expiry/review conditions with durable entries. Validate migrations before reading old state into a new runtime.

## Worked example

An old checkpoint says a migration is pending. The repository has since changed. Resume by checking the recorded revision and current state; do not repeat the migration solely because the remembered plan says so.

## Try it and check the result

Design two threads for different projects. Write a synthetic private marker to one and verify the other cannot retrieve it. Expire a memory entry and confirm it is excluded from future retrieval, while preserving audit records according to the retention policy.

## Tradeoffs and limits

Summarization is lossy. In-memory stores do not prove restart durability. Deletion from retrieval is different from deletion from backups; state which was tested.

## Sources and interpretation

[LangGraph: persistence](https://docs.langchain.com/oss/python/langgraph/persistence) distinguishes thread persistence from cross-thread stores. [Anthropic: context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) describes durable notes and context management.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Cold-Session Checkpoint](Cold-Session%20Checkpoint.md)
- [Context Compaction Contract](Context%20Compaction%20Contract.md)
- [Retry and Idempotency Contract](../08%20-%20Agent%20Runtime/Retry%20and%20Idempotency%20Contract.md)
