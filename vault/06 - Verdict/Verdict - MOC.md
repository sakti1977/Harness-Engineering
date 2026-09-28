---
type: moc
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - verdict
  - moc
---

# Verdict - MOC

**What evidence proves each claim, beyond "tests pass"?**

Verdict is where most agent failures surface: a green check that observed the wrong thing. The controls here turn "done" from a statement into a gate: claims are written first, each names the check that proves it at the right boundary, and state changes require current evidence from someone other than the author.

## In this repository

- `docs/proof-matrix.md`: one row per claim, with the required and tested boundary; the checker fails a gap once verification is requested.
- `docs/proof-gaps.md`: a claim checklist, eight gap types and an audit.
- `scripts/harness_transition.py`: planner, worker and verifier roles; `passing` needs an independent verifier and evidence newer than the code.
- `harness-tests/`: every gate is itself tested against a defect fixture and a clean fixture.

## Notes

- [[Claim-to-Proof Matrix]]
- [[Verification Routes and Test Fidelity]]
- [[Feature Ledger as a Gate]]
- [[First Divergence and Failure Packet]]
- [[Traces Metrics and Privacy]]
- [[Harness-Control Tests]]

Return to [[Five Layers of a Harness]] or [[Harness Engineering - MOC]].
