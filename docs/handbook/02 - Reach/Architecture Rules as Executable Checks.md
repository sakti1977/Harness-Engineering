---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
---

# Architecture Rules as Executable Checks

## Problem and mechanism

A dependency rule in prose can be repeatedly violated. Translate a stable boundary into a deterministic check with a repair message, while keeping design rationale in the handbook. This checks the chosen structural rule, not architectural quality in general.

## Worked exercise

Suppose domain code must not import the HTTP presentation layer. In a disposable Python fixture, parse imports with the standard-library AST module. Add a forbidden import and expect a failure naming the file, imported module and intended dependency direction. Add a permitted import and expect success. Check aliases, relative imports and package initializers before broadening the claim.

Do not use a text search as proof of semantic import coverage: dynamic imports, generated modules and runtime plugin loading may evade it. Document these limitations or use a language-aware tool with demonstrated coverage. Keep exceptions local, explained and reviewable.

## Evidence and limits

[OpenAI’s harness engineering account](https://openai.com/index/harness-engineering/) describes mechanical dependency-boundary checks. This import exercise is a local design and has not been implemented or executed in this release. Apply such checks when a stable recurring rule justifies their maintenance cost.

See [AGENTS.md as a Map](AGENTS.md%20as%20a%20Map.md), [Knowledge Base Maintenance](Knowledge%20Base%20Maintenance.md) and [Harness-Control Tests](../10%20-%20Harness%20Testing/Harness-Control%20Tests.md).
