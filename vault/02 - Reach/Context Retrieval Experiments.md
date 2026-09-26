---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Context Retrieval Experiments

## Problem

Loading every file can bury the relevant constraint; retrieving too little can hide the cause of a bug.

## Mechanism

Compare three strategies on the same tasks: preload selected documents, retrieve on demand from a compact index, and a hybrid. Record which required facts were available before the first edit, irrelevant content volume, discovery time and final correctness. Keep the underlying repository snapshot fixed.

## Worked example

A timezone defect needs the public API contract and the persistence conversion path. An index that finds only the API file is incomplete even if it uses fewer tokens. A repository map is a candidate retrieval strategy, not the grading oracle.

## Try it and check the result

Choose three past bugs with known dependency paths. Hide the fixes, specify the required facts privately, and compare plain search with a repository map. Count missed facts and incorrect edits; inspect the traces before declaring a winner.

## Tradeoffs and limits

Tiny local experiments are diagnostic. They do not establish a universal context size or retrieval policy. A retrieved malicious instruction remains untrusted even when its search score is high.

## Sources and interpretation

[Anthropic: context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) discusses retrieval tradeoffs. [Aider](https://github.com/Aider-AI/aider) provides a repository-map implementation to inspect.

The worked example and exercise are local teaching designs unless identified as executed in [[Vault Update Record]]. Source findings do not establish that this design is best for every project.

## Connected concepts

- [[Repository Discovery Funnel]]
- [[Untrusted Content and Prompt Injection]]
- [[Harness Ablation Experiments]]
