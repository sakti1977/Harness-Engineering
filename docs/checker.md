# Checker contract

Run `python3 scripts/harness_check.py --help` from the repository root. Python 3.10+ is required. `--root` selects an existing project directory; the default is this checkout. `--format json` provides a machine-readable result. `--adapter copilot` additionally checks `.github/copilot-instructions.md`.

## What is checked

Six readable, nonempty regular files: authority, scope, proof matrix and readiness documents under `docs/`, plus checkpoint and feature JSON under `.harness/`. Artifacts resolving outside the inspected project are rejected. Markdown contents are not semantically graded.

The feature contract lives in [the schema](../schemas/feature.schema.json). The implementation supports the specific schema subset used there and also rejects blank strings and nonrelative/traversing expected-surface paths. It is not a general JSON Schema engine.

Required fields: `id`, `outcome`, `state`, `expected_surface`, `exclusions`, `verification`, `claims`. Unknown fields, wrong types, blank required strings, duplicate list items and missing required list items are rejected. Exclusions may be empty. Expected-surface paths need not exist yet because they may be planned additions.

Allowed states: `planned`, `active`, `blocked`, `ready_for_verification`. Self-attested `passing` is intentionally rejected. An independently evidenced completion transition is not implemented; this checker should not be used as a permanent feature-lifecycle system.

## Output and limits

Exit 0: artifact checks passed. Exit 1: artifact/ledger failures. Exit 2: invalid CLI usage or project root. JSON output includes `schema_version`, `scope`, `ok`, `findings` and `limitations`.

The verification field is descriptive text; it is never executed. A valid ledger does not mean its command is safe or that its claims are true. Review and run trusted commands separately. No readiness probe, changed-file scope check, sandbox enforcement or live-agent evaluation is performed.
