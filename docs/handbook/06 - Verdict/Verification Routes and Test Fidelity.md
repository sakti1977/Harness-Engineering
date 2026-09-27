---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - verdict
---

# Verification Routes and Test Fidelity

## Core idea and problem
A run proves only the path it exercised. Sequential and mocked tests can miss production races.

## How it works
Route fields Claim, Entry, Boundaries, Setup, Actions, Observations, Cleanup. Check entry/state/timing/response/persistence fidelity. Create concurrent requests before awaiting; inspect responses and shared DB.

## Example / failure mode
Coaching reads chart version 1, the user corrects their birth time, and coaching still writes against version 1: a sequential test never opens that window.

## Implementation and verification notes
A faithful red E2E test is a successful harness detection; keep feature active.

## Connected concepts
- [Claim-to-Proof Matrix](Claim-to-Proof%20Matrix.md)
- [Readiness Contract](../04%20-%20Ground/Readiness%20Contract.md)
- [First Divergence and Failure Packet](First%20Divergence%20and%20Failure%20Packet.md)

## Practical extension

The repository's `docs/verify.md` writes each route down with seven fields (claim, entry, boundaries, setup, actions, observations, cleanup) and compares it on five fidelity checks (entry, state, timing, response, persistence). `python3 -m examples.astro.sweep` injects the competing write at every step, and `python3 -m examples.astro.ablation` weakens one fidelity dimension at a time to show which weakenings produce a false pass.


Run a helper check and persistent-state checks on the same broken implementation to see the proof gap. See [First Executable Harness Lab](../11%20-%20Practical%20Implementations/First%20Executable%20Harness%20Lab.md) for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [Source Coverage Index](../00%20-%20Start%20Here/Source%20Coverage%20Index.md).
