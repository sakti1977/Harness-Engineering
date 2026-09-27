# Harness Engineering

**Your coding agent's tests pass. The bug still ships.**

This kit shows why in one command, and gives you the small, checkable controls around an AI coding agent (context, permissions, environment, proof and memory) that catch it.

[![Checks](https://github.com/sakti1977/Harness-Engineering/actions/workflows/checks.yml/badge.svg)](https://github.com/sakti1977/Harness-Engineering/actions/workflows/checks.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

![Demo: a helper test passes on a broken booking app, two outcome checks catch the double booking, all six pass on the fix](assets/demo.svg)

## Try it in 10 seconds

Requires Python 3.10+. No model key, no dependency installation, no external service.

```sh
git clone https://github.com/sakti1977/Harness-Engineering.git
cd Harness-Engineering
python3 -m examples.booking.demo
```

A helper test passes on a broken booking application, the kind of green check an agent happily reports as "done". Two outcome checks then catch the duplicate booking it missed, and all six checks pass on the fixed version. The middle failures are intentional; `LAB PASSED` means the runner observed the expected failures and the successful fix. [Read the lab](docs/handbook/11%20-%20Practical%20Implementations/First%20Executable%20Harness%20Lab.md).

This is a local SQLite example, including concurrent connections. It does not demonstrate a deployed HTTP API or production readiness.

## Why this exists

I lead engineering teams building US healthcare software, and I use coding agents on my own projects. On one of them, a local 1-on-1 coaching app for managers, my Copilot enhancements were taking one to two hours each and landed right about 60% of the time. The model was not the problem; the environment around it was. After adding the five controls in this kit, a typical enhancement took 10 to 15 minutes and landed about 95% of the time. Those are my own working observations on one project, not a benchmark. This repository packages the controls so you can test them on yours.

## The five layers

| Layer | Question it answers | Starter artifact |
| --- | --- | --- |
| **Reach** | Can the agent find the right context and the owner of the behavior? | [Copilot instructions](.github/copilot-instructions.md) |
| **Power** | What may it run, edit or touch, and what is off limits? | [Authority policy](docs/authority.md), [scope contract](docs/scope-contract.md) |
| **Ground** | Does it work in an environment that is ready and reproducible? | [Readiness contract](docs/readiness.md) |
| **Verdict** | What evidence proves each claim, beyond "tests pass"? | [Proof matrix](docs/proof-matrix.md), [feature ledger](.harness/feature.json) |
| **Carry** | Can a fresh session pick up where the last one stopped? | [Checkpoint](.harness/checkpoint.md) |

Reach, Power, Ground, Verdict and Carry are this project's organizing synthesis, not an industry standard. [Source history](docs/handbook/00%20-%20Start%20Here/Source%20Coverage%20Index.md) separates inherited teaching material from newly cited primary sources.

## Check your own project

```sh
python3 scripts/harness_check.py --root /path/to/project
python3 scripts/harness_check.py --root /path/to/project --format json
python3 scripts/harness_check.py --adapter copilot
python3 scripts/harness_check.py --root /path/to/project --session --base main
```

The checker is read-only: it checks six core artifacts, nonempty files and the feature ledger's structure, types, states and relative paths. The optional Copilot check adds its instruction file. It **never executes** a project's verification string. `--session` adds read-only git queries: changed files against the feature's scope, and claims against recorded evidence. It does not verify readiness, enforce permissions or judge what a change means. [Checker contract](docs/checker.md).

## Make "done" a gate, not a memo

An agent that can write `passing` into a feature list will. The next session then trusts it. The ledger here only changes state through a transition policy, and every change lands in a hash-chained audit log that the checker replays.

```sh
python3 -m examples.gate.demo
```

```text
REFUSED  Agent marks its own work passing
         TRANSITION_NOT_ALLOWED: active -> passing. Allowed from active: blocked, ready_for_verification.
REFUSED  Agent asks for verification
         SCOPE_OUTSIDE_SURFACE src/billing.py: Not in expected_surface: amend the scope with a reason, or revert.
REFUSED  Same agent approves its own request
         TRANSITION_NOT_INDEPENDENT: copilot-agent requested verification and cannot approve it
RECORDED Independent verifier approves with evidence
STALE    Next session changes verified code: passing is flagged stale
```

Check a live session against its contract at any time with `python3 scripts/harness_check.py --session`. Roles are declared, not authenticated: pair this with CODEOWNERS or branch protection on the log. [Transition policy and limits](docs/transitions.md).

## Choose your route

- **Learn:** [learning path](docs/handbook/00%20-%20Start%20Here/Learning%20Path.md) and [complete handbook](docs/handbook/00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md).
- **Adopt:** [project assessment](docs/handbook/11%20-%20Practical%20Implementations/Project%20Harness%20Assessment.md), [adoption guide](docs/adoption.md) and [filled templates](templates/core/README.md).
- **Evaluate:** [agent evaluation suite](docs/handbook/10%20-%20Harness%20Testing/Agent%20Evaluation%20Suite.md), [experiment template](docs/handbook/Templates/Experiment%20Template.md) and [source register](docs/handbook/00%20-%20Start%20Here/Source%20Register.md).
- **Use Obsidian:** open `vault/` as a vault. No community plugin is required.

## What is included

- Tool-neutral artifact validation with actionable failures and JSON output.
- Session scope checks and a feature transition gate with an append-only audit log.
- A versioned feature schema and negative regression fixtures.
- A model-free booking demonstration with persisted-state and concurrency assertions.
- A source-backed learning handbook, repository pattern atlas and reusable note templates.
- GitHub Actions checks, documentation export and link checks.

### Repository layout

| Path | What it is |
| --- | --- |
| `examples/booking/` | The runnable failure-to-fix lab |
| `examples/gate/` | The transition-gate demo |
| `scripts/` | The checker, transition command, handbook exporter and doc checks |
| `templates/core/` | Filled starter artifacts to copy into your project |
| `vault/` | The handbook source, written as an Obsidian vault (edit here) |
| `docs/handbook/` | The same handbook generated from `vault/` with GitHub-friendly links (do not edit) |

## Development checks

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest examples.booking.test_booking -v
python3 -m examples.booking.demo
python3 -m examples.gate.demo
python3 scripts/export_handbook.py --check
python3 scripts/check_docs.py
```

See [contributing](CONTRIBUTING.md), [security scope](SECURITY.md), [roadmap](docs/roadmap.md) and [verification record](docs/verification.md). Live-model benchmarks, automatic installation, production sandboxing and tested multi-vendor runtime adapters remain future work.

## Try it and tell me what broke

The most useful thing you can do is run the demo, point the checker at a real project, and [open an issue](https://github.com/sakti1977/Harness-Engineering/issues/new/choose) with what happened: where you got stuck, what the checker missed, or a failure from your own agent that this kit does not catch yet. Independent results are worth more than anything else here. If the kit helped, a star helps other engineers find it.

## Reuse

Code and original documentation are licensed under [MIT](LICENSE). Linked external sources retain their own terms.
