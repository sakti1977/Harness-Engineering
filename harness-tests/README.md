# Harness tests

The harness is code, and code can be wrong. These tests check that every gate catches the defect it promises to catch and still passes clean work.

```sh
python3 harness-tests/run.py
```

For each entry in [`manifest.json`](manifest.json), the runner copies a fixture to a scratch directory, commits it to a fresh git repository, applies the named defect from [`defects.py`](defects.py), calls the real gate function, and compares the receipt with the expected one. A receipt is the sorted list of failure codes the gate returned; an empty list means it passed. The output is only what failed:

```text
FAIL transition-self-approval: expected ['TRANSITION_NOT_INDEPENDENT'] received PASS
Harness tests: 66 entries, 1 problem(s).
```

## The rule

**A new gate ships with a defect fixture and a clean fixture, or it does not ship.** The gate is not the deliverable; the gate plus its two tests is. The runner enforces it:

| Check | Fails when |
| --- | --- |
| `UNCOVERED` | a failure code appears in `scripts/harness_check.py`, `scripts/harness_transition.py`, `scripts/harness_handoff.py` or `scripts/harness_attempt.py` with no manifest entry expecting it |
| `NO_CLEAN_FIXTURE` | the `artifacts`, `session`, `transition`, `handoff`, `resume` or `attempt` gate has no entry it must pass |
| `FIXTURE_DRIFT` | a fixture lacks a core artifact, its ledger no longer matches the schema, or its proof matrix lacks the columns the checker reads |
| `FAIL` | a gate returned a different receipt than expected |

## Where it runs

- On every push and pull request, in [checks.yml](../.github/workflows/checks.yml).
- Weekly on a schedule, in [harness-tests.yml](../.github/workflows/harness-tests.yml), because fixtures drift when the repository they describe moves underneath them. A fixture that no longer resembles the codebase gives the same false green you started with.

## Adding a gate

1. Give the gate a failure code and emit it from the gate.
2. Add a defect function to `defects.py` that breaks exactly one thing (setup may use real transitions).
3. Add a manifest entry expecting the code, and make sure a clean entry for that gate still passes.
4. Run `python3 harness-tests/run.py`. Until both entries exist, it reports `UNCOVERED`.

`tests/test_harness_tests.py` tests the runner itself: it disables real gates and checks that the runner reports them, and that uncovered codes, missing clean fixtures and drifted fixtures are caught.
