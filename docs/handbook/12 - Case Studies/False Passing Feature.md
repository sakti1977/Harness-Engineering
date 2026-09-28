---
type: case-study
evidence_kind: instructional-scenario with a measured counterpart
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - case-studies
---

# False Passing Feature

> **Evidence status:** the original scenario (a feature marked `passing` after a narrow green test while the end-to-end check fails) is inherited teaching material. The measured counterpart below comes from this repository's own evaluation pilot: small, one author, Claude models only.

## Problem

An agent runs the test it wrote, sees green, and reports the feature done. The end-to-end behavior is still broken. The next session trusts the record and builds on it, and the false state spreads.

## What the pilot measured

`evals/jyotish` gives agents the three Jyotish Coach user reports, with and without the harness, and grades outcomes with a hidden grader the agent cannot read. In the 2026-09-27 pilot (two runs per cell):

| Model | Said "all fixed" while a hidden check failed, without harness | With harness |
| --- | --- | --- |
| Claude Haiku 4.5 | 2 of 2 runs | 0 of 2 |
| Claude Sonnet | 0 of 2 | 0 of 2 |
| Claude Opus | 0 of 2 | 0 of 2 |

Both Haiku runs without the harness fixed two bugs, missed the race, and reported everything fixed. Run 1 decided the race was a symptom of the sync bug; run 2 filtered stale coaching out of the read path but still stored it. In both, the agent's own tests passed without crossing the boundary where the defect lived. With the harness, every run reached `ready_for_verification` and none tried to mark the feature `passing` or wrote the verifier's evidence file.

## Controls that stop it

- The transition policy refuses `active -> passing` and requires an independent verifier ([Feature Ledger as a Gate](../06%20-%20Verdict/Feature%20Ledger%20as%20a%20Gate.md)).
- The proof-plan gate refuses verification while a claim's producer misses its required boundary ([Claim-to-Proof Matrix](../06%20-%20Verdict/Claim-to-Proof%20Matrix.md)).
- Evidence goes stale when verified files change (`PASSING_STALE`), so the next session is not handed an old verdict.

## Reproduce it

```sh
python3 -m examples.gate.demo
python3 evals/jyotish/prepare.py --out ~/eval-runs --condition bare --name mine
```

The results page in `evals/jyotish/results/` lists every limit of the pilot. Run it with your own agent before generalising from it.

## Connected concepts

- [Feature Ledger as a Gate](../06%20-%20Verdict/Feature%20Ledger%20as%20a%20Gate.md)
- [Claim-to-Proof Matrix](../06%20-%20Verdict/Claim-to-Proof%20Matrix.md)
- [Agent Evaluation Suite](../10%20-%20Harness%20Testing/Agent%20Evaluation%20Suite.md)
- [Case Study Template](../Templates/Case%20Study%20Template.md)
