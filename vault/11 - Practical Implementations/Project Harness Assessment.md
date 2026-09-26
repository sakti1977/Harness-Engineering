---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Project Harness Assessment

## Problem

A project needs a prioritized next improvement, not every available agent framework.

## Mechanism

Start with one recent failure. Check discoverability, authority, environment, outcome evidence and continuity. For each control record missing, documented, configured, exercised or enforced—with evidence and scope. Choose the smallest change that addresses the failure and define its negative test.

## Worked example

A repository has an authority document but no execution boundary. Mark authority as documented. A checker finding the file cannot promote it to enforced.

## Try it and check the result

From the GitHub checkout run `python3 scripts/harness_check.py --root /path/to/project --format json`. It only inspects this kit’s expected artifacts and ledger schema; it does not execute project commands. Missing files are adoption findings, not proof the project is unsafe. Use [[Task Contract Template]] to plan the next change.

## Tradeoffs and limits

The checker is a narrow read-only assessment, not a universal maturity score. Existing project conventions may satisfy the same purpose through different files. Adapt the mapping before copying templates.

## Sources and interpretation

[OpenAI: harness engineering](https://openai.com/index/harness-engineering/) and [Anthropic: long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) provide engineering context. The assessment levels and CLI are local project design.

The worked example and exercise are local teaching designs unless identified as executed in [[Vault Update Record]]. Source findings do not establish that this design is best for every project.

## Connected concepts

- [[Five Layers of a Harness]]
- [[Minimal Harness Adoption Path]]
- [[First Executable Harness Lab]]
