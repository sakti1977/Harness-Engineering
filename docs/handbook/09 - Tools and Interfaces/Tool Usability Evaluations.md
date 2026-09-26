---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Tool Usability Evaluations

## Problem

A tool can be implemented correctly yet repeatedly confuse the agent selecting or calling it.

## Mechanism

Test tool names, descriptions, argument schemas and output shape on realistic tasks. Track wrong-tool selection, invalid arguments, redundant calls, output size, latency and task outcome. Change one design choice at a time and keep a held-out set.

## Worked example

A log tool returns every event from every service. A bounded query with service, run ID and time range can make the relevant error easier to find. Measure lost information as well as reduced output.

## Try it and check the result

Create a small task where the required log entry is known. Compare a full dump with a filtered response. Count calls and missed facts. Include an empty-result case and a truncated-result case with explicit continuation metadata.

## Tradeoffs and limits

Shorter output is not automatically better. Stable IDs and truthful truncation matter. Tool performance varies with the model and task; do not teach one naming scheme as universal.

## Sources and interpretation

[Anthropic: writing effective tools](https://www.anthropic.com/engineering/writing-tools-for-agents) motivates realistic tool evaluation and useful, bounded responses.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Tool Extension Contract](Tool%20Extension%20Contract.md)
- [Context Retrieval Experiments](../02%20-%20Reach/Context%20Retrieval%20Experiments.md)
- [Typed Outputs and Semantic Validation](Typed%20Outputs%20and%20Semantic%20Validation.md)
