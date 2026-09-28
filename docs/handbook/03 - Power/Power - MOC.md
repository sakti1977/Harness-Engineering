---
type: moc
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - power
  - moc
---

# Power - MOC

**What may the agent read, write and run, and what stays off limits?**

Capability and permission are different things. The model can do almost anything; the harness decides what this session may do. Power controls are strongest when they are enforced by a tool or a gate, and weakest when they only live in an instruction file.

## In this repository

- `docs/authority.md` states the policy and, crucially, which mechanism enforces each rule.
- `harness_check.py --session` compares changed files with the feature's `expected_surface` and `excluded_paths`.
- The transition gate refuses state changes outside the policy, so an agent cannot widen its own authority by editing the ledger.

## Notes

- [Authority Policy](Authority%20Policy.md)
- [Secret Handling](Secret%20Handling.md)
- [Sandbox Enforcement Matrix](Sandbox%20Enforcement%20Matrix.md)
- [MCP Identity and Network Boundaries](MCP%20Identity%20and%20Network%20Boundaries.md)
- [Untrusted Content and Prompt Injection](Untrusted%20Content%20and%20Prompt%20Injection.md)
- [Scope Contract](../05%20-%20Scope/Scope%20Contract.md)

Return to [Five Layers of a Harness](../01%20-%20Foundations/Five%20Layers%20of%20a%20Harness.md) or [Harness Engineering - MOC](../00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md).
