---
type: moc
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - ground
  - moc
---

# Ground - MOC

**Does the work run in an environment that is ready and faithful to production?**

A check proves only what its environment allows it to observe. A test that runs in one time zone, against a per-test mock, or one call at a time cannot see bugs that live in another time zone, a shared store or an overlap. Ground is about making the environment faithful to the claim, and ready before work starts.

## In this repository

- The five fidelity checks in `docs/verify.md` (entry, state, timing, response, persistence) compare a route with the product's real execution.
- The Jyotish lab's age claim is tested at four UTC offsets because the real incident only appeared behind UTC.
- `docs/readiness.md` describes readiness probes. It is documentation only in this release; an executable readiness runner is on the roadmap.

## Notes

- [Readiness Contract](Readiness%20Contract.md)
- [Initialization Session](Initialization%20Session.md)
- [Reproducible Evaluation Environment](Reproducible%20Evaluation%20Environment.md)
- [Verification Routes and Test Fidelity](../06%20-%20Verdict/Verification%20Routes%20and%20Test%20Fidelity.md)

Return to [Five Layers of a Harness](../01%20-%20Foundations/Five%20Layers%20of%20a%20Harness.md) or [Harness Engineering - MOC](../00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md).
