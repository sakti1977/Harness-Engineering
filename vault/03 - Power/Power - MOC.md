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

- [[Authority Policy]]
- [[Secret Handling]]
- [[Sandbox Enforcement Matrix]]
- [[MCP Identity and Network Boundaries]]
- [[Untrusted Content and Prompt Injection]]
- [[Scope Contract]]

Return to [[Five Layers of a Harness]] or [[Harness Engineering - MOC]].
