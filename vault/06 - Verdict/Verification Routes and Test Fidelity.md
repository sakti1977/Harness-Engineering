---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - verdict
---

# Verification Routes and Test Fidelity

## Problem

A run proves only the path it exercised. Sequential tests cannot open a race window, mocked stores cannot reject a write, and a test pinned to one time zone cannot see an off-by-one-day age. The run is green and honest about what it did; the gap is between what it did and what the claim needs.

## Mechanism

A verification route is the smallest run that crosses every boundary a claim depends on. Write it in seven fields: **claim, entry, boundaries, setup, actions, observations, cleanup**. Then compare it with production on five fidelity checks:

| Check | Question |
| --- | --- |
| Entry | Does it call the same entry point real callers use? |
| State | Do all actions share one store? |
| Timing | Does it preserve the ordering or overlap that can change the result? |
| Response | Does it assert exact visible outcomes, not "any status below 500"? |
| Persistence | Does it read the lasting state back? |

A route that fails one check is a different route and proves less. A faithful route that goes red is the harness working: the feature stays `active`.

## Worked example

The stale-coaching route in `docs/verify.md`: coaching reads the chart at version 1, pauses, the user saves a corrected birth time, then coaching writes. The observation is a 409 for the losing request and no coaching row whose chart version differs from the current one at write time. A sequential test (generate, then correct) never opens that window and passes on the broken app.

## Try it

```sh
python3 -m examples.astro.sweep      # inject the correction at every step of generation
python3 -m examples.astro.ablation   # weaken one fidelity check at a time
```

The sweep shows which interleavings expose the race. The ablation shows which weakenings turn the route into a false pass on the broken app, and which still catch it.

## Limits

A route is a hypothesis about where the claim can fail; it is only as good as the boundaries you listed. Deterministic pauses stand in for real scheduling and cannot prove the absence of every interleaving. Record the environment actually exercised ([[Readiness Contract]]), and when a route fails, report the first divergence rather than the last symptom ([[First Divergence and Failure Packet]]).

## Connected concepts

- [[Claim-to-Proof Matrix]]
- [[Readiness Contract]]
- [[First Executable Harness Lab]]
- [[Harness Ablation Experiments]]
