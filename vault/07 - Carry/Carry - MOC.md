---
type: moc
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - carry
  - moc
---

# Carry - MOC

**Can a fresh session pick up where the last one stopped?**

Every session ends, often mid-task, and the next one starts with no memory of the conversation. Carry controls externalize state before context disappears, anchor each handoff to code and evidence, make recovery executable, and treat a stale handoff as a failed check rather than as guidance.

## In this repository

- `python3 scripts/harness_handoff.py --write` drafts the checkpoint from the observed repository, including uncommitted work.
- `--check` is the last action of a session; `--resume` is the first, and it fails when the checkpoint no longer matches the repository.
- The transition log is an append-only, hash-chained record of who changed the feature's state, when and why.

## Notes

- [[Cold-Session Checkpoint]]
- [[Append-Only Journal]]
- [[Context Compaction Contract]]
- [[Resume Replay and Fork]]
- [[Memory Scope and Retention]]

Return to [[Five Layers of a Harness]] or [[Harness Engineering - MOC]].
