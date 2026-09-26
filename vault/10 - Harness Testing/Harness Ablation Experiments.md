---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Harness Ablation Experiments

## Problem

Adding memory, reviewers or instructions can improve one task while increasing cost or causing regressions elsewhere.

## Mechanism

Record a baseline, one hypothesized mechanism, fixed task/environment/model settings and an acceptance rule before running. Compare a changed variant and, when useful, removal of a control. Use optimization tasks for iteration and held-out tasks for the acceptance decision.

## Worked example

A new pre-completion reminder catches missing tests but causes timeouts on short tasks. Report both categories and the extra cost. Decide whether a conditional reminder serves the goal better.

## Try it and check the result

Fill [[Experiment Template]]. Include raw run IDs, success numerator/denominator, stop reasons, elapsed time and cost. Re-run after model upgrades. Mark the experiment unexecuted until raw evidence exists.

## Tradeoffs and limits

Repeated inspection of holdouts makes them part of optimization. Record exposure and refresh them. Small differences can be noise; do not claim causality when multiple mechanisms changed together.

## Sources and interpretation

[LangChain: Better Harness](https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals) describes iterative evaluation and held-outs; [Anthropic: harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps) motivates reassessing scaffolding.

The worked example and exercise are local teaching designs unless identified as executed in [[Vault Update Record]]. Source findings do not establish that this design is best for every project.

## Connected concepts

- [[Agent Evaluation Suite]]
- [[Reproducible Evaluation Environment]]
- [[Budgets and Termination]]
