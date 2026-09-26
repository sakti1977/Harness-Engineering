---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Traces Metrics and Privacy

## Problem

A final score cannot explain where a run failed, while unrestricted transcripts may expose private data.

## Mechanism

Attach run, parent, task and tool-call identifiers to events. Record start/end times, status, stop reason, retry count and usage. Separate provider-reported cost from estimates. Collect content only for an explicit debugging need; redact before persistence and define retention and access rules.

## Worked example

A run times out after three retries. Its trace should show which operation failed first and whether it may have taken effect. The final timeout alone cannot establish whether repeating the action is safe.

## Try it and check the result

Take a synthetic trace and find the first divergence using only event IDs and statuses. Inject a fake secret marker and ensure the exported diagnostic excludes it. Verify child tool events connect to their parent run.

## Tradeoffs and limits

Trace collection has overhead and privacy costs. Redaction is fallible, so minimize captured data. OpenTelemetry GenAI conventions are marked Development; pin a version before relying on exact field names.

## Sources and interpretation

[OpenTelemetry: agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) defines evolving agent/tool spans. [OpenAI: harness engineering](https://openai.com/index/harness-engineering/) describes agent-accessible observability. The minimal event selection here is a local design.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [First Divergence and Failure Packet](First%20Divergence%20and%20Failure%20Packet.md)
- [Retry and Idempotency Contract](../08%20-%20Agent%20Runtime/Retry%20and%20Idempotency%20Contract.md)
- [Secret Handling](../03%20-%20Power/Secret%20Handling.md)
