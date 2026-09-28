---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - verdict
---

# Claim-to-Proof Matrix

## Problem

"Tests pass" is a statement about the tests, not about the feature. A helper test can pass while the real route never calls the helper; a response check can pass while nothing was stored. When "done" is not broken into claims, nobody can say which claim a green run actually proved.

## Mechanism

Write the feature's outcome as separate, falsifiable claims. For each claim, record four things:

| Column | Question |
| --- | --- |
| Claim | What must be true, in words a user would recognise? |
| Required boundary | Where does it become true or false: `unit`, `entry`, `persistence`, `concurrency`, `environment`, `external`, `ui`? |
| Evidence producer | Which named test or route produces the proof? |
| Tested boundary | Which boundaries does that producer actually cross? |

A gap is any required boundary the producer does not cross. Outcome evidence supports a claim; diagnostic evidence only explains a failure; a contradiction (a failing observation at the required boundary) vetoes `passing` whatever else is green.

## Worked example

The Jyotish Coach claim "saving a profile reports synced only when the profile is stored" requires `entry` and `persistence`. The weak check asserts the response said `synced: true`: it crosses `entry` only, so the matrix shows a `persistence` gap before any code runs. That is exactly the gap behind the real incident, a "Synced" badge over rejected writes. The strong route reads the profile back from a new connection and forces one failed write.

## Try it

```sh
python3 scripts/harness_check.py            # PROOF_BOUNDARY_GAP / PROOF_PRODUCER_MISSING are advisory here
python3 scripts/harness_transition.py --to ready_for_verification --actor me --role worker --reason "done"
```

The second command refuses while any claim has a gap or no producer. `docs/proof-matrix.md` holds this repository's matrix; `docs/proof-gaps.md` is the procedure: weak-to-strong claim rewrites, eight gap types (boundary, state, negative, timing, fidelity, oracle, staleness, attribution) and a six-step audit.

## Limits

The checker compares the boundaries you declare; it cannot tell whether a producer really crosses them. That judgement belongs to the route in [[Verification Routes and Test Fidelity]] and to an independent verifier. A grader can also be wrong: check that it rejects a plausible broken fix and accepts a valid alternative ([[Grader Reliability]]).

## Connected concepts

- [[Verification Routes and Test Fidelity]]
- [[Feature Ledger as a Gate]]
- [[Scope Contract]]
- [[Jyotish Coach Sync and Age Incidents]]
