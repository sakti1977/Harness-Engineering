---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - ground
---

# Readiness Contract

## Problem

A test run against an unusable environment produces a meaningless green. An empty database cannot show a collision; a machine in one time zone cannot show an age that is wrong behind UTC; a missing service turns every call into a mocked success. The agent then spends the session "fixing" code against a broken floor.

## Mechanism

Initialization is a gate, not a repair bot. Before feature work, run probes and report each as `PASS`, `FAIL` or `SKIP`:

- the runtime and version are supported;
- configuration is usable without exposing secrets;
- required seed or test data exists;
- the real service boundary is reachable;
- the baseline verification command can judge the system (it goes red on a known defect).

`READY` means every required probe passed. When a prerequisite fails, dependent probes `SKIP`, the command exits nonzero, and feature work stays blocked. Each probe names its recovery step.

## Worked example

For the Jyotish lab, the environment probe that matters is time: the age claim needs the eve of a birthday evaluated at several UTC offsets (UTC+5:30, UTC, UTC-5, UTC-10). A readiness check that only confirms "tests run" passes in India and misses the real incident, where users behind UTC saw their age a day early. The baseline probe is the demo itself: `python3 -m examples.astro.demo` must show the weak checks green and the outcome checks red on the broken app before any fix is trusted.

## Try it

Write the probes for one of your projects in `docs/readiness.md` (the adopted template has the format). Add one probe that runs the verification command against a known-broken commit and expects it to fail.

## Limits

This kit ships the contract format, not a probe runner: probes are project commands, and the checker never executes project code. A passing probe proves only the environment it ran in; record that environment with the evidence ([Reproducible Evaluation Environment](Reproducible%20Evaluation%20Environment.md)).

## Connected concepts

- [Initialization Session](Initialization%20Session.md)
- [Claim-to-Proof Matrix](../06%20-%20Verdict/Claim-to-Proof%20Matrix.md)
- [Verification Routes and Test Fidelity](../06%20-%20Verdict/Verification%20Routes%20and%20Test%20Fidelity.md)
- [Jyotish Coach Sync and Age Incidents](../12%20-%20Case%20Studies/Jyotish%20Coach%20Sync%20and%20Age%20Incidents.md)
