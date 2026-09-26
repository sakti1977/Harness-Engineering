# Harness Engineering

A practical kit for improving the environment around an AI coding agent: context, permissions, execution, verification and durable state.

**Start with a real failure. Add a small control. Verify that it catches the failure.**

## Try the failure-to-fix demonstration

Requires Python 3.10+. No model key, dependency installation or external service.

```sh
git clone https://github.com/sakti1977/Harness-Engineering.git
cd Harness-Engineering
python3 -m examples.booking.demo
```

You will see a helper test pass on a broken booking application, two outcome checks catch duplicate bookings, and all six checks pass on the fixed version. The middle failures are intentional; `LAB PASSED` means the runner observed the expected failures and the successful fix.

This is a local SQLite example, including concurrent connections. It does not demonstrate a deployed HTTP API or production readiness. [Read the lab](docs/handbook/11%20-%20Practical%20Implementations/First%20Executable%20Harness%20Lab.md).

## Choose your route

- **Learn:** [Learning path](docs/handbook/00%20-%20Start%20Here/Learning%20Path.md) and [complete handbook](docs/handbook/00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md).
- **Adopt:** [project assessment](docs/handbook/11%20-%20Practical%20Implementations/Project%20Harness%20Assessment.md), [adoption guide](docs/adoption.md) and [filled templates](templates/core/README.md).
- **Evaluate:** [agent evaluation suite](docs/handbook/10%20-%20Harness%20Testing/Agent%20Evaluation%20Suite.md), [experiment template](docs/handbook/Templates/Experiment%20Template.md) and [source register](docs/handbook/00%20-%20Start%20Here/Source%20Register.md).
- **Use Obsidian:** open `vault/` as a vault. No community plugin is required. GitHub-friendly navigation is generated from those same notes.

## Check this starter or inspect your project

```sh
python3 scripts/harness_check.py
python3 scripts/harness_check.py --root /path/to/project --format json
python3 scripts/harness_check.py --adapter copilot
```

The checker is read-only: it checks six core artifacts, nonempty files and the feature ledger’s structure, types, states and relative paths. The optional Copilot check adds its instruction file. It **never executes** a project's verification string. It does not verify readiness, enforce permissions, inspect code changes or establish task completion. [Checker contract](docs/checker.md).

## What is included

- Tool-neutral artifact validation with actionable failures and JSON output.
- A versioned feature schema and negative regression fixtures.
- A model-free booking demonstration with persisted-state and concurrency assertions.
- A source-backed learning vault, repository pattern atlas and reusable note templates.
- GitHub Actions checks, documentation export and link checks.

The Reach / Power / Ground / Verdict / Carry vocabulary is this project's organizing synthesis, not an industry standard. [Source history](docs/handbook/00%20-%20Start%20Here/Source%20Coverage%20Index.md) distinguishes inherited teaching material from newly cited primary sources.

## Development checks

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest examples.booking.test_booking -v
python3 -m examples.booking.demo
python3 scripts/export_handbook.py --check
python3 scripts/check_docs.py
```

See [contributing](CONTRIBUTING.md), [security scope](SECURITY.md), [roadmap](docs/roadmap.md) and [verification record](docs/verification.md). Live-model benchmarks, automatic installation, production sandboxing and tested multi-vendor runtime adapters remain future work.

## Reuse

Code and original documentation are licensed under [MIT](LICENSE). Linked external sources retain their own terms. If the kit helps, share a reproducible case study or a source correction; independent results are especially useful.
