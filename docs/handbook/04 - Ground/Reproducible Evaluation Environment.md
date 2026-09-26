---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Reproducible Evaluation Environment

## Problem

An apparent harness improvement can actually be a faster machine, different dependency or leftover task state.

## Mechanism

Record task revision, harness revision, model identifier and configuration, dependency lock/image digest, OS, CPU/RAM, timeout, concurrency, seed and network assumptions. Reset mutable state per trial. Give each run a unique ID; record cache inputs, not only output scores.

## Worked example

Two variants run the same test, but one inherits yesterday’s database. Its higher success rate cannot be attributed to the changed prompt. Reinitialize both environments and distinguish infrastructure failures from behavioral failures.

## Try it and check the result

Use [Experiment Template](../Templates/Experiment%20Template.md) to specify two identical local runs. Change only a resource limit, then inspect whether the failure occurred before the agent acted or during task execution. Preserve both outcomes; do not quietly discard inconvenient timeouts.

## Tradeoffs and limits

Pinning reduces variation but cannot make a hosted model perfectly reproducible. Report unavailable details as unknown. Resource allocation is part of the tested configuration.

## Sources and interpretation

[Anthropic: infrastructure noise](https://www.anthropic.com/engineering/infrastructure-noise) reports infrastructure effects. [SWE-bench](https://github.com/SWE-bench/SWE-bench) documents reproducible evaluation and run-cache caveats.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Readiness Contract](Readiness%20Contract.md)
- [Agent Evaluation Suite](../10%20-%20Harness%20Testing/Agent%20Evaluation%20Suite.md)
- [Harness Ablation Experiments](../10%20-%20Harness%20Testing/Harness%20Ablation%20Experiments.md)
