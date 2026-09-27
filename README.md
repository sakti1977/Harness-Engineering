# Harness Engineering

**Your coding agent's tests pass. The bug still ships.**

This kit shows why in one command, and gives you the small, checkable controls around an AI coding agent (context, permissions, environment, proof and memory) that catch it.

[![Checks](https://github.com/sakti1977/Harness-Engineering/actions/workflows/checks.yml/badge.svg)](https://github.com/sakti1977/Harness-Engineering/actions/workflows/checks.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

![Demo: three weak checks pass on a broken astrology coaching app, three outcome checks catch the defects, all pass on the fix](assets/demo.svg)

## Try it in 10 seconds

Requires Python 3.10+. No model key, no dependency installation, no external service.

```sh
git clone https://github.com/sakti1977/Harness-Engineering.git
cd Harness-Engineering
python3 -m examples.astro.demo
```

The lab models [Jyotish Coach](https://github.com/sakti1977/astro-coach), a Vedic astrology app I am building: it takes a user's birth details, builds their chart and coaches behavioural and attitude changes grounded in it. Three weak checks pass on a broken version, the kind of green an agent happily reports as "done":

| Defect | Weak check (green on the broken app) | Outcome check that catches it |
| --- | --- | --- |
| "Synced" badge while nothing was stored (a real incident) | The save returned synced | Read the profile back; force a rejected write |
| Ages a day early for users behind UTC (a real incident) | Age tested in IST only | Eve of the birthday at UTC+5:30, UTC, UTC-5, UTC-10 |
| Coaching stored against a chart the user just corrected | Coaching generated sequentially | Pause coaching after its read, correct the birth time, then let it write |

The middle failures are intentional; `LAB PASSED` means the runner saw every expected failure and the successful fix. This is a local, standard-library SQLite model, not the production app and not real astronomy. [Read the lab](examples/astro/README.md).

## Why this exists

I lead engineering teams building US healthcare software, and I use coding agents on my own projects. On one of them, a local 1-on-1 coaching app for managers, my Copilot enhancements were taking one to two hours each and landed right about 60% of the time. The model was not the problem; the environment around it was. After adding the five controls in this kit, a typical enhancement took 10 to 15 minutes and landed about 95% of the time. Those are my own working observations on one project, not a benchmark. The lab's defects come from a second project of mine, Jyotish Coach. This repository packages the controls so you can test them on yours.

## The five layers

| Layer | Question it answers | Starter artifact |
| --- | --- | --- |
| **Reach** | Can the agent find the right context and the owner of the behavior? | [Copilot instructions](.github/copilot-instructions.md) |
| **Power** | What may it run, edit or touch, and what is off limits? | [Authority policy](docs/authority.md), [scope contract](docs/scope-contract.md) |
| **Ground** | Does it work in an environment that is ready and reproducible? | [Readiness contract](docs/readiness.md) |
| **Verdict** | What evidence proves each claim, beyond "tests pass"? | [Proof matrix](docs/proof-matrix.md), [verification routes](docs/verify.md), [proof gaps guide](docs/proof-gaps.md), [feature ledger](.harness/feature.json) |
| **Carry** | Can a fresh session pick up where the last one stopped? | [Checkpoint](.harness/checkpoint.md), [handoff gate and Resume Protocol](docs/handoff.md), [agent instructions](AGENTS.md) |

Reach, Power, Ground, Verdict and Carry are this project's organizing synthesis, not an industry standard. [Source history](docs/handbook/00%20-%20Start%20Here/Source%20Coverage%20Index.md) separates inherited teaching material from newly cited primary sources.

## Adopt it in your project

```sh
python3 scripts/harness_adopt.py --root /path/to/project            # preview; writes nothing
python3 scripts/harness_adopt.py --root /path/to/project --apply    # create missing files; never overwrites
```

It adds the core contracts, a first feature to fill in, verification routes, agent instructions with the Resume Protocol and, with `--ci`, a GitHub Actions workflow. Your project can be in any language. [Adoption guide](docs/adoption.md).

## Check your own project

```sh
python3 scripts/harness_check.py --root /path/to/project
python3 scripts/harness_check.py --root /path/to/project --format json
python3 scripts/harness_check.py --adapter copilot
python3 scripts/harness_check.py --root /path/to/project --session --base main
```

The checker is read-only: it checks six core artifacts, nonempty files and the feature ledger's structure, types, states and relative paths. The optional Copilot check adds its instruction file. It **never executes** a project's verification string. `--session` adds read-only git queries: changed files against the feature's scope, and claims against recorded evidence. It does not verify readiness, enforce permissions or judge what a change means. [Checker contract](docs/checker.md).

## A run only proves what it exercised

A green run proves the path it took and nothing else. Each claim gets a written [verification route](docs/verify.md): entry, boundaries, setup, actions, observations and cleanup, so a fresh session reruns the real journey instead of a convenient one. Failures name the claim, the route, what was expected and observed, and where to repair.

```sh
python3 -m examples.astro.sweep      # inject the birth-time correction at every step of coaching
python3 -m examples.astro.ablation   # weaken the route one dimension at a time
```

```text
Broken app stored stale coaching at 11 of 13 points; fixed app at 0.
A sequential run only tests 'start' or 'after_write': both are ok on the broken app.

run sequentially                               always red
run sequentially, test edited to expect 201    FALSE PASS
separate store per actor, any status < 500     FALSE PASS
accept any status < 500                        discriminates
status < 500 and no state check                FALSE PASS
```

Find the gaps in your own checks with the [proof gaps guide](docs/proof-gaps.md).

## Hand off honestly

Sessions end with work in progress. `python3 scripts/harness_handoff.py --write` records the repository as it is (uncommitted files included, no ceremonial commit), lists only claims with current evidence as verified, and keeps suspicions apart from facts. `--check` is the last action of a session; `--resume` is the first, and it treats a checkpoint that no longer matches the repository as a failed check instead of following it. [Handoff gate and Resume Protocol](docs/handoff.md).

## Test the harness itself

Every gate here is code, and code can be wrong. [`harness-tests/`](harness-tests/README.md) runs each gate against a named defect (a forged log entry, a self-approval, a helper-only proof row, an edit outside scope) and against clean work, and compares the exact failure codes. It runs on every change and weekly, and it fails when a gate emits a code that no defect fixture covers: a new gate ships with a defect fixture and a clean fixture, or it does not ship.

```sh
python3 harness-tests/run.py
```

## Make "done" a gate, not a memo

An agent that can write `passing` into a feature list will. The next session then trusts it. The ledger here only changes state through a transition policy, and every change lands in a hash-chained audit log that the checker replays.

```sh
python3 -m examples.gate.demo
```

```text
REFUSED  Agent marks its own work passing
         TRANSITION_NOT_ALLOWED: active -> passing. Allowed from active: blocked, ready_for_verification.
REFUSED  Agent asks for verification
         SCOPE_OUTSIDE_SURFACE app/support/upi.py: Not in expected_surface: amend the scope with a reason, or revert.
REFUSED  Same agent approves its own request
         TRANSITION_NOT_INDEPENDENT: copilot-agent requested verification and cannot approve it
RECORDED Independent verifier approves with evidence
STALE    Next session changes verified code: passing is flagged stale
```

Check a live session against its contract at any time with `python3 scripts/harness_check.py --session`. Roles are declared, not authenticated: pair this with CODEOWNERS or branch protection on the log. [Transition policy and limits](docs/transitions.md).

## Choose your route

- **Learn:** [learning path](docs/handbook/00%20-%20Start%20Here/Learning%20Path.md) and [complete handbook](docs/handbook/00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md).
- **Adopt:** `scripts/harness_adopt.py`, the [adoption guide](docs/adoption.md), [project assessment](docs/handbook/11%20-%20Practical%20Implementations/Project%20Harness%20Assessment.md) and [filled templates](templates/core/README.md).
- **Evaluate:** [agent evaluation suite](docs/handbook/10%20-%20Harness%20Testing/Agent%20Evaluation%20Suite.md), [experiment template](docs/handbook/Templates/Experiment%20Template.md) and [source register](docs/handbook/00%20-%20Start%20Here/Source%20Register.md).
- **Use Obsidian:** open `vault/` as a vault. No community plugin is required.

## What is included

- Tool-neutral artifact validation with actionable failures and JSON output.
- Session scope checks and a feature transition gate with an append-only audit log.
- A versioned feature schema and negative regression fixtures.
- A model-free Jyotish Coach lab with persisted-state, time-zone and concurrency claims, verification routes, an interleaving sweep and a fidelity ablation.
- A source-backed learning handbook, repository pattern atlas and reusable note templates.
- GitHub Actions checks, documentation export and link checks.

### Repository layout

| Path | What it is |
| --- | --- |
| `examples/astro/` | The Jyotish Coach failure-to-fix lab, sweep and ablation |
| `examples/gate/` | The transition-gate demo |
| `scripts/` | The adopt, checker, transition, handoff and handbook commands, and doc checks |
| `harness-tests/` | Defect and clean fixtures that test every gate, with a coverage rule |
| `templates/core/` | Filled starter artifacts to copy into your project |
| `vault/` | The handbook source, written as an Obsidian vault (edit here) |
| `docs/handbook/` | The same handbook generated from `vault/` with GitHub-friendly links (do not edit) |

## Development checks

```sh
python3 -m unittest discover -s tests -v
python3 harness-tests/run.py
python3 -m unittest examples.astro.test_astro -v
python3 -m examples.astro.demo
python3 -m examples.astro.sweep
python3 -m examples.astro.ablation
python3 -m examples.gate.demo
python3 scripts/export_handbook.py --check
python3 scripts/check_docs.py
```

See [contributing](CONTRIBUTING.md), [security scope](SECURITY.md), [roadmap](docs/roadmap.md) and [verification record](docs/verification.md). Live-model benchmarks, production sandboxing and tested multi-vendor runtime adapters remain future work.

## Try it and tell me what broke

The most useful thing you can do is run the demo, point the checker at a real project, and [open an issue](https://github.com/sakti1977/Harness-Engineering/issues/new/choose) with what happened: where you got stuck, what the checker missed, or a failure from your own agent that this kit does not catch yet. Independent results are worth more than anything else here. If the kit helped, a star helps other engineers find it.

## Reuse

Code and original documentation are licensed under [MIT](LICENSE). Linked external sources retain their own terms.
