---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Agent Evaluation Suite

## Problem

One successful attempt does not show that an agent reliably solves a class of tasks.

## Mechanism

Define each task’s initial state, permitted actions, expected outcome, grader, timeout and reset procedure. A trial is one execution. A capability suite explores unsolved work; a regression suite protects behavior already achieved. Keep deterministic control checks separately runnable without a model.

## Worked example

A task succeeds on 6 of 10 recorded attempts. Report 6/10 with conditions and failures. Success in at least one of several attempts answers a different question from success on every attempt. Do not calculate either from a single cherry-picked run.

## Try it and check the result

Convert [False Passing Feature](../12%20-%20Case%20Studies/False%20Passing%20Feature.md) into a task specification with a final database assertion. Use [Experiment Template](../Templates/Experiment%20Template.md) to record trial outcomes, cost and stop reason. Execute live trials only when a model and budget are explicitly configured.

## Tradeoffs and limits

No live-agent benchmark has been run for this update. A small task bank is a starting point, not a population estimate. Avoid overfitting by preserving held-out cases and human-checking graders.

## Sources and interpretation

[Anthropic: agent evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) supports tasks, trials, outcomes and suite distinctions.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Agent Harness and Evaluation Harness](../01%20-%20Foundations/Agent%20Harness%20and%20Evaluation%20Harness.md)
- [Grader Reliability](Grader%20Reliability.md)
- [Harness Ablation Experiments](Harness%20Ablation%20Experiments.md)
