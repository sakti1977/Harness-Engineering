# Checker contract

Run `python3 scripts/harness_check.py --help` from the repository root. Python 3.10+ is required. `--root` selects an existing project directory; the default is this checkout. `--format json` provides a machine-readable result. `--adapter copilot` additionally checks `.github/copilot-instructions.md`.

## What is checked

Six readable, nonempty regular files: authority, scope, proof matrix and readiness documents under `docs/`, plus checkpoint and feature JSON under `.harness/`. Artifacts resolving outside the inspected project are rejected. Markdown contents are not semantically graded.

The feature contract lives in [the schema](../schemas/feature.schema.json). The implementation supports the specific schema subset used there and also rejects blank strings and nonrelative/traversing expected-surface paths. It is not a general JSON Schema engine.

Required fields: `id`, `outcome`, `state`, `expected_surface`, `exclusions`, `verification`, `claims`. Unknown fields, wrong types, blank required strings, duplicate list items and missing required list items are rejected. Exclusions may be empty. Expected-surface paths need not exist yet because they may be planned additions.

Allowed states: `planned`, `active`, `blocked`, `ready_for_verification`, `passing`. `passing` is accepted only when a verified transition log ends there; self-attested `passing` is rejected. Optional `excluded_paths` lists paths or globs the task must not touch. When `.harness/feature-log.jsonl` exists, every run replays it against the [transition policy](transitions.md) using read-only git queries.

## Proof matrix

The first table in `docs/proof-matrix.md` with the columns Claim, Required boundary, Evidence producer and Tested boundary is read as the proof plan. Every claim in the feature ledger needs a row with an evidence producer, and the tested boundaries (`unit`, `entry`, `persistence`, `concurrency`, `environment`, `external`, `ui`) must include every required one. Findings are advisory (INFO) while the feature is planned, active or blocked, and fail once it is `ready_for_verification` or `passing`. The checker trusts the boundary columns as written; it does not read the tests. See [proof gaps and acceptance claims](proof-gaps.md).

## Session mode

`--session` adds read-only git queries (hooks, fsmonitor, external diff and textconv disabled):

- Every file changed since `--base` (default `HEAD`: uncommitted and untracked work) must match `expected_surface` and must not match `excluded_paths`. Entries are an exact file, a directory prefix, or a glob. Files under `.harness/` are always in scope.
- Free-text `exclusions` are printed as a manual review reminder.
- Each claim is checked against `.harness/evidence.json`. The latest entry per claim must pass, name a commit in the repository, and no project file may have changed since it. When the state is `ready_for_verification` an unproven claim fails; otherwise it is reported as pending.

```text
FAIL SCOPE_OUTSIDE_SURFACE src/billing.py
  Not in expected_surface: amend the scope with a reason, or revert.
Session: 1 file(s) outside scope, 0 in excluded paths, 0 of 4 claim(s) proven.
```

State changes go through `scripts/harness_transition.py`; see [feature transitions](transitions.md).

## Output and limits

Exit 0: artifact checks passed. Exit 1: artifact/ledger failures. Exit 2: invalid CLI usage or project root. JSON output includes `schema_version`, `scope`, `ok`, `findings` and `limitations`.

The verification field is descriptive text; it is never executed. A valid ledger does not mean its command is safe or that its claims are true. Review and run trusted commands separately. No readiness probe, sandbox enforcement or live-agent evaluation is performed. Session mode compares file paths, not the meaning of a change.
