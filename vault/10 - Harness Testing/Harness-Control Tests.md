---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - harness-testing
---

# Harness-Control Tests

## Problem

A green gate can mean it works, or that it never looked at the defect. A scope gate that diffs the wrong revision prints OK forever. A gate that always refuses looks strict in every demo. Controls need tests of their own, and those tests must not depend on a live model.

## Mechanism

Test the control, not the agent. For each gate, keep two kinds of fixture:

- a **defect fixture**: a seeded repository with one named defect, which the gate must refuse with an exact failure code;
- a **clean fixture**: correct work, which the gate must pass.

Compare receipts exactly (the sorted list of codes), so a gate that returns the right code for the wrong reason, or an extra code, fails. Mutation-test the gate: replace it with "always allow" and "always deny" and confirm the suite goes red both ways. A rejected transition or write must leave every file byte-identical.

## Worked example

`harness-tests/` runs 66 manifest entries across five gates (`artifacts`, `session`, `transition`, `handoff`, `resume`). Each copies `fixtures/clean-project`, commits it to a fresh repository, applies a defect from `defects.py`, calls the real gate function, and compares receipts. Coverage rules keep it honest:

| Check | Fails when |
| --- | --- |
| `UNCOVERED` | a failure code in the gate scripts has no fixture expecting it |
| `NO_CLEAN_FIXTURE` | a gate has no entry it must pass |
| `FIXTURE_DRIFT` | a fixture no longer matches the schema or the checker's columns |

Adding a failure code without a fixture fails the build.

## Try it

```sh
python3 harness-tests/run.py
```

Then disable one refusal, for example the independence check in `scripts/harness_transition.py`, and run it again: `FAIL transition-self-approval: expected ['TRANSITION_NOT_INDEPENDENT'] received PASS`. `tests/test_harness_tests.py` tests the runner itself the same way.

## Limits

Deterministic fixtures prove the gate's logic, not that an agent will run the gate. Whether agents follow the protocol is a stochastic question for live trials ([[Agent Evaluation Suite]]); keep the two suites separate so a flaky model run never hides a broken gate.

## Connected concepts

- [[Authority Policy]]
- [[Feature Ledger as a Gate]]
- [[Safe Exact-Anchor Editing]]
- [[Agent Evaluation Suite]]
