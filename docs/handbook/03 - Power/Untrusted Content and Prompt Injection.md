---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Untrusted Content and Prompt Injection

## Problem

An agent can encounter instructions inside material it was asked to read. Treating that material as authority can redirect its actions.

## Mechanism

Preserve the origin of repository text, retrieved pages and tool outputs. Limit available actions and data independently of the model’s judgment. Validate proposed effects at the execution boundary; keep credentials outside the task environment where feasible. Tool-result summaries and delegated findings retain the trust level of their underlying sources.

## Worked example

A test log says to upload a local configuration file to repair the build. The log is evidence about a test, not permission to send data. The user’s task and the tool policy still determine allowable actions.

## Try it and check the result

In a disposable fixture, place a harmless request to write an out-of-scope marker in a fake tool result. Check both the proposed action and the filesystem afterward. A model ignoring this one instruction is a behavioral result; a denied write through every enabled route tests a stronger boundary.

## Tradeoffs and limits

Prompt wording, classifiers and source labels are partial defenses. Do not generalize a few attack fixtures into a security guarantee. This exercise uses a local marker, no real secrets or external transmission.

## Sources and interpretation

[Anthropic: prompt injection defenses](https://www.anthropic.com/news/prompt-injection-defenses) documents the threat and layered defenses. [Anthropic: containment](https://www.anthropic.com/engineering/how-we-contain-claude) explains environmental containment and source trust. This fixture is a local teaching proposal.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Authority Policy](Authority%20Policy.md)
- [Sandbox Enforcement Matrix](Sandbox%20Enforcement%20Matrix.md)
- [MCP Identity and Network Boundaries](MCP%20Identity%20and%20Network%20Boundaries.md)
