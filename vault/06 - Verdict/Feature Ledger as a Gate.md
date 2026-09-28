---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - verdict
---

# Feature Ledger as a Gate

## Problem

A feature list the agent can edit freely is a memo, not a control. The agent that wrote the code marks it `passing`; the next session reads `passing` and builds on it. The ledger has become a false memory with the authority of a record.

## Mechanism

Treat the ledger (`.harness/feature.json`) as state that only a policy may change:

- **States:** `planned`, `active`, `blocked`, `ready_for_verification`, `passing`.
- **Roles:** the planner owns scope; the worker requests verification; the verifier owns the verdict.
- **Gates:** `ready_for_verification` needs the scope gate (no changed file outside `expected_surface`) and the proof-plan gate (every claim has a matrix row with a producer and no gap). `passing` needs a verifier who did not request verification, passing evidence for every claim, and no project file changed since the evidence was recorded.
- **Audit log:** every transition appends to `.harness/feature-log.jsonl`, each entry hashing the previous one. The checker replays the log on every run.

A refused transition changes no file.

## Worked example

`python3 -m examples.gate.demo` plays the shortcuts an agent takes:

| Attempt | Result |
| --- | --- |
| `active -> passing` directly | `TRANSITION_NOT_ALLOWED` |
| Request verification with an out-of-scope file changed | `SCOPE_OUTSIDE_SURFACE` |
| Verifier approves with no evidence | refused by the evidence gate |
| Approve its own request | `TRANSITION_NOT_INDEPENDENT` |
| Change verified code in the next session | `PASSING_STALE` |

## Try it

Run the demo. Then, in this repository, set `"state": "passing"` in `.harness/feature.json` by hand and run `python3 scripts/harness_check.py`: `PASSING_WITHOUT_LOG`, because `passing` is accepted only through a verified transition log. In a project with a log, a hand-edited state that disagrees with the replay is `STATE_MISMATCH`, and a rewritten past entry is `LOG_CHAIN_BROKEN` or `LOG_REWRITTEN`. Restore with `git checkout -- .harness/`.

## Limits

Roles are declared, not authenticated: an agent can pass `--role verifier`. The log makes that visible after the fact; it does not prevent it. Pair it with repository review rules (CODEOWNERS on `.harness/`, branch protection) and a verifier that is a different person or process. `docs/transitions.md` has the full policy table.

## Connected concepts

- [[Claim-to-Proof Matrix]]
- [[Scope Contract]]
- [[Harness-Control Tests]]
- [[False Passing Feature]]
- [[Append-Only Journal]]
