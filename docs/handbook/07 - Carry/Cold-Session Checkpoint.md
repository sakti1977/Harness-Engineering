---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - carry
---

# Cold-Session Checkpoint

## Problem

Sessions end mid-task: context runs out, the laptop closes, a different agent picks up tomorrow. "Mostly implemented, a few edge cases left" loses the diagnosis and invites the next session to repeat work or contradict a decision. Worse, a handoff written from memory can claim more than the repository shows.

## Mechanism

Write the checkpoint (`.harness/checkpoint.md`) from the observed repository, not from recollection, and make it answer eight questions for a session with no history:

1. What is the active outcome and state?
2. Which revision, and which files are uncommitted?
3. What is verified, and by what?
4. What is not verified since the last edit?
5. What are the suspected causes (kept apart from verified facts)?
6. What blocks progress, and which commands are still to run?
7. Which decisions must be preserved?
8. What is the first command and the next bounded edit?

`--write` fills the observable parts. The hand-written parts (causes, blockers, decisions, next edit) survive rewrites. `--check` is the gate at the end of a session; `--resume` is the first action of the next.

## Worked example

A session diagnoses the stale-coaching race but runs out of time before fixing it. A weak handoff says "race mostly fixed". A checkpoint says: revision `a31c872`, `examples/astro/astro.py` uncommitted; claim "coaching started before a correction is not stored against the old chart" **not verified since the last edit**; suspected cause: the write does not compare chart versions; first command `python3 -m unittest examples.astro.test_astro -v`; next edit: make the coaching insert conditional on the chart version read.

## Try it

```sh
python3 scripts/harness_handoff.py --write
python3 scripts/harness_handoff.py --check    # CHECKPOINT_MISSING_FIELD: the next bounded edit is still TODO
# write the next edit under "## Next bounded edit" in .harness/checkpoint.md, then:
python3 scripts/harness_handoff.py --check    # Handoff check passed.
echo "# edit" >> examples/astro/astro.py
python3 scripts/harness_handoff.py --resume   # CHECKPOINT_STALE: the handoff is a failed check, not guidance
git checkout -- examples/astro/astro.py .harness/checkpoint.md
```

## Limits

The checkpoint can verify what it observes (revision, files, state, evidence freshness) and the presence of the hand-written sections. It cannot verify that a suspected cause is right or that the next edit is wise. A never-written template means "no handoff yet", which `--resume` reports and `--check` refuses.

## Connected concepts

- [Append-Only Journal](Append-Only%20Journal.md)
- [Resume Replay and Fork](Resume%20Replay%20and%20Fork.md)
- [Recovery Audit](../02%20-%20Reach/Recovery%20Audit.md)
- [Cold Session Loses Diagnosis](../12%20-%20Case%20Studies/Cold%20Session%20Loses%20Diagnosis.md)
- [Memory Scope and Retention](Memory%20Scope%20and%20Retention.md)
