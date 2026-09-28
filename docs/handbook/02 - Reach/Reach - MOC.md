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

- [AGENTS.md as a Map](AGENTS.md%20as%20a%20Map.md)
- [Repository as Shared Context](Repository%20as%20Shared%20Context.md)
- [Repository Discovery Funnel](Repository%20Discovery%20Funnel.md)
- [Recovery Audit](Recovery%20Audit.md)
- [Context Retrieval Experiments](Context%20Retrieval%20Experiments.md)
- [Architecture Rules as Executable Checks](Architecture%20Rules%20as%20Executable%20Checks.md)
- [Knowledge Base Maintenance](Knowledge%20Base%20Maintenance.md)

Return to [Five Layers of a Harness](../01%20-%20Foundations/Five%20Layers%20of%20a%20Harness.md) or [Harness Engineering - MOC](../00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md).
