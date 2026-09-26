---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Delegation and Shared State

## Problem

More agents can add integration cost and shared-file conflicts faster than they add useful work.

## Mechanism

Delegate bounded tasks with owned outputs, explicit dependencies, evidence requirements and an integration owner. Preserve parent/child trace IDs and source provenance. Define failure, timeout and cancellation handling. Compare against one agent using the same total budget.

## Worked example

One worker investigates a dependency and another writes an isolated fixture. The parent integrates their findings. Two workers editing the same configuration without ownership are a different workload and need serialization or conflict detection.

## Try it and check the result

Create a task contract using [Task Contract Template](../Templates/Task%20Contract%20Template.md). Inject one child timeout and one contradictory conclusion. Verify the parent records the conflict and does not mark integration complete merely because other children succeeded.

## Tradeoffs and limits

Parallelism is useful for separable work; tightly coupled changes may be slower. A child’s summary is not higher-trust evidence than its sources. No live multi-agent speedup is demonstrated by this vault.

## Sources and interpretation

[Anthropic: multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system) reports workload-specific benefits and overhead. [SDK research demo](https://github.com/anthropics/claude-agent-sdk-demos/blob/main/research-agent/README.md) illustrates lineage.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Safe Exact-Anchor Editing](../09%20-%20Tools%20and%20Interfaces/Safe%20Exact-Anchor%20Editing.md)
- [Traces Metrics and Privacy](../06%20-%20Verdict/Traces%20Metrics%20and%20Privacy.md)
- [Scope Contract](../05%20-%20Scope/Scope%20Contract.md)
