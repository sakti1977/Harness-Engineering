---
type: lab
status: locally-verified
reviewed: 2026-09-27
evidence_kind: executed-synthetic-fixture
---

# First Executable Harness Lab

## What you will learn

A green check can coexist with a broken product when it observes the wrong thing. This lab models three defects from Jyotish Coach, a Vedic astrology coaching app: a "Synced" badge while nothing was stored, ages a day early for users behind UTC, and coaching stored against a chart the user had just corrected. Weak checks stay green on all three; outcome checks at the right boundary catch them.

## Requirements and scope

Python 3.10 or newer; no model, API key, package install or network service. Tests create and clean temporary SQLite databases. The ephemeris is a deterministic stand-in, the coaching text is templated rather than generated, and there is no web server: the lab is a model of the app's flow, not the production app.

## Run inside this vault

Open a terminal at the vault root:

```sh
cd Labs
python3 -m examples.astro.demo
```

From a GitHub repository checkout, run the same modules from its root:

```sh
python3 -m examples.astro.demo
python3 -m examples.astro.sweep
python3 -m examples.astro.ablation
```

The supplied code is [the app model](../Labs/examples/astro/astro.py), [weak and outcome checks](../Labs/examples/astro/test_astro.py), [the demonstration runner](../Labs/examples/astro/demo.py), [the interleaving sweep](../Labs/examples/astro/sweep.py) and [the fidelity ablation](../Labs/examples/astro/ablation.py).

## Read the result

1. Three weak checks pass on the broken app: the save response says synced, the age is right in IST, and sequential coaching succeeds.
2. Three outcome checks fail as expected, each with a message naming the claim, its verification route, what was expected, what was observed and where to repair.
3. All outcome checks pass on the fixed app, which commits before reporting synced, parses date-only birth dates without a UTC conversion, and writes coaching only if the chart version it read is still current.
4. The runner reports `LAB PASSED` only if exactly those failures occur and the fixed checks succeed.

The sweep injects the birth-time correction at every step of coaching generation: the broken app stores stale coaching at 11 of 13 points, and the two points a sequential run can reach both look fine. The ablation weakens the route one dimension at a time and shows which weakenings let the defect ship.

## Adapt the lesson

Pick one claim your harness verifies with a unit command. List its real entry point, shared state, environment, relevant timing, visible response and lasting side effect. Write it as a verification route, keep a deliberately defective variant, and confirm the route fails on it. Do not claim this SQLite model proves production behavior.

The example is original teaching code based on incidents recorded in the app's own rules file; see [Jyotish Coach Sync and Age Incidents](../12%20-%20Case%20Studies/Jyotish%20Coach%20Sync%20and%20Age%20Incidents.md). [Anthropic's evaluation article](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) supplies the outcome-grading motivation; it did not author or validate this fixture. See [Verification Routes and Test Fidelity](../06%20-%20Verdict/Verification%20Routes%20and%20Test%20Fidelity.md), [Failure to Evaluation Workflow](../10%20-%20Harness%20Testing/Failure%20to%20Evaluation%20Workflow.md), [Grader Reliability](../10%20-%20Harness%20Testing/Grader%20Reliability.md) and [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md).
