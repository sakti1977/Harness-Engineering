---
type: lab
status: locally-verified
reviewed: 2026-09-26
evidence_kind: executed-synthetic-fixture
---

# First Executable Harness Lab

## What you will learn

A green helper test can coexist with duplicate persisted bookings. Verify the response and final database state at the boundary that matters. This lab uses local SQLite connections, including two concurrent requests; it is not a deployed HTTP service.

## Requirements and scope

Python 3.10 or newer; no model, API key, package install or network service. Tests create and clean temporary databases. Doctor and slot are simple text keys: interval overlap, timezones, authentication and production deployment are outside this exercise.

## Run inside this vault

Open a terminal at the vault root:

```sh
cd Labs
python3 -m examples.booking.demo
```

From a GitHub repository checkout, run the same module directly from its root:

```sh
python3 -m examples.booking.demo
```

The supplied code is [the booking implementation](../Labs/examples/booking/booking.py), [outcome assertions](../Labs/examples/booking/test_booking.py), and [the demonstration runner](../Labs/examples/booking/demo.py).

## Read the result

1. The weak helper check passes on the deliberately broken implementation.
2. Two stronger checks fail as expected: duplicate rejection/persistence and concurrent single-winner behavior. The broken variant returns two successes and stores two rows.
3. All six checks pass on the fixed implementation, whose database uniqueness constraint rejects the second identical doctor/slot pair.
4. The runner reports `LAB PASSED` only if those exact expected failures occur and the fixed checks succeed. Its exit code is zero for the successful demonstration.

Seeing `FAILED (failures=2)` in the middle is intentional. Unexpected failures or a broken variant that slips through make the demo exit nonzero.

## Run only the fixed checks

From `Labs` in the vault, or the GitHub checkout root:

```sh
python3 -m unittest examples.booking.test_booking -v
```

## Adapt the lesson

Replace the slot model with your real domain invariant and keep a deliberately defective variant. For an actual API, add an HTTP-level assertion and inspect the real persistence boundary. Do not claim this SQLite fixture proves production behavior.

The example is original teaching code. [Anthropic’s evaluation article](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) supplies the outcome-grading motivation; it did not author or validate this fixture. See [[Failure to Evaluation Workflow]], [[False Passing Feature]], [[Grader Reliability]] and [[Vault Update Record]].
