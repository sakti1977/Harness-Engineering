---
type: moc
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - reach
  - moc
---

# Reach - MOC

**Can the agent find the right context and the owner of the behavior?**

Reach fails quietly: the agent finds a plausible file and edits it, while the code that actually owns the behavior sits elsewhere. More documentation does not fix this; a short map with routes to the right places does, and so does testing whether a fresh session can follow it.

## In this repository

- `AGENTS.md` is the root map: global rules, where the feature ledger and routes live, and the commands to run. `CLAUDE.md` and the Copilot instructions point to it.
- `docs/verify.md` routes each claim to its real entry point, so the agent tests the path callers use.
- `python3 scripts/harness_handoff.py --resume` doubles as a recovery audit: a fresh session must answer eight questions from files and commands.

## Notes

- [[AGENTS.md as a Map]]
- [[Repository as Shared Context]]
- [[Repository Discovery Funnel]]
- [[Recovery Audit]]
- [[Context Retrieval Experiments]]
- [[Architecture Rules as Executable Checks]]
- [[Knowledge Base Maintenance]]

Return to [[Five Layers of a Harness]] or [[Harness Engineering - MOC]].
