---
type: case-study
evidence_kind: instructional-scenario with executable fixtures
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - case-studies
---

# Cold Session Loses Diagnosis

> **Evidence status:** the scenario is inherited teaching material; no production incident is claimed. The controls that address it have executable fixtures in this repository.

## Problem

A session works out why a bug happens (a write that does not check the chart version, say) and decides how to fix it. The diagnosis lives in the chat. The session ends. The next agent reads "race mostly fixed", reopens a settled decision, and spends an hour rediscovering the cause, or worse, trusts a claim that was never verified.

## What goes wrong

| Handoff says | Repository shows | Consequence |
| --- | --- | --- |
| "Almost done" | An uncommitted file nobody mentioned | The next session commits or discards work it does not understand |
| "Race fixed" | No passing evidence since the last edit | An unverified claim is treated as done |
| Nothing about the decision | Two plausible fixes | The next agent picks the other one |
| A revision | A newer commit | The guidance describes a repository that no longer exists |

## Controls

- The checkpoint is written from the observed repository (`harness_handoff.py --write`) and keeps verified facts apart from suspected causes ([[Cold-Session Checkpoint]]).
- The handoff gate (`--check`) refuses a checkpoint that overclaims, hides an unverified claim, or has no specific next edit.
- The Resume Protocol (`--resume`) is the first action of the next session; a stale checkpoint is reported as a failed check, not followed.

## Reproduction

The `handoff` and `resume` fixtures in `harness-tests/manifest.json` reproduce each row: `handoff-overclaim`, `handoff-hides-unverified`, `handoff-next-edit-blank`, `handoff-accidental-edit`, `resume-after-edit`, `resume-after-commit`, `resume-after-state-change` and `resume-evidence-outdated`.

```sh
python3 harness-tests/run.py
```

In the evaluation pilot, one harness run wrote its checkpoint before changing the feature's state; the gate reported it stale, which is this control catching a real ordering mistake.

## Connected concepts

- [[Cold-Session Checkpoint]]
- [[Append-Only Journal]]
- [[Recovery Audit]]
- [[Case Study Template]]
