---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Failure to Evaluation Workflow

## Problem

A failure report that ends in a prompt edit can recur because nothing checks the repaired behavior.

## Mechanism

Capture the first divergence and minimal initial state. Remove sensitive data, classify the failure, and write an outcome assertion. Preserve a broken variant and a clean variant. After fixing the mechanism, add a regression case and record the result.

## Worked example

A helper-level check missed a persistent double booking. The regression checks the response and row count, then proves the assertion detects the intentionally broken implementation.

## Try it and check the result

Run [First Executable Harness Lab](../11%20-%20Practical%20Implementations/First%20Executable%20Harness%20Lab.md). Explain which weak check stays green and which invariant catches the error. Use [Case Study Template](../Templates/Case%20Study%20Template.md) to distinguish the synthetic reproduction from a real incident.

## Tradeoffs and limits

One fixture protects one modeled failure. Deduplicating cases improves maintenance, but preserve distinct causes. An example containing production data must be sanitized before publication.

## Sources and interpretation

[LangChain: Better Harness](https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals) uses failures and traces to guide evaluations. The local booking fixture is a synthetic teaching example.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [First Divergence and Failure Packet](../06%20-%20Verdict/First%20Divergence%20and%20Failure%20Packet.md)
- [Case Studies - MOC](../12%20-%20Case%20Studies/Case%20Studies%20-%20MOC.md)
- [Grader Reliability](Grader%20Reliability.md)
