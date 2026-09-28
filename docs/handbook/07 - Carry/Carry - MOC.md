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

- [Cold-Session Checkpoint](Cold-Session%20Checkpoint.md)
- [Append-Only Journal](Append-Only%20Journal.md)
- [Context Compaction Contract](Context%20Compaction%20Contract.md)
- [Resume Replay and Fork](Resume%20Replay%20and%20Fork.md)
- [Memory Scope and Retention](Memory%20Scope%20and%20Retention.md)

Return to [Five Layers of a Harness](../01%20-%20Foundations/Five%20Layers%20of%20a%20Harness.md) or [Harness Engineering - MOC](../00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md).
