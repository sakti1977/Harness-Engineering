# Changelog

## Unreleased

**Added**

- Adopt writes instruction files for Gemini CLI (`GEMINI.md`) and Cursor (`.cursor/rules/harness.mdc`), and `--agents` takes a comma-separated list, for example `--agents claude,cursor`.
- CI on macOS and Windows as well as Linux.
- A code of conduct, a social preview image, and issue template links for security reports and evaluation results.
- Twenty core handbook notes rewritten around the executable examples, with a `status` label on every note saying how far to trust it.

**Fixed**

- On macOS and Windows, where temporary directories are symlinks or short names, the handoff and resume gates refused every project with `artifact resolves outside project`. Project roots are now resolved before comparison.
- All file reads and writes use UTF-8 explicitly, instead of the Windows default code page.

## v0.2.0 (2026-09-28)

The kit goes from checking files to gating work: a feature can only be called done with evidence, and every gate is tested against the defect it promises to catch.

**Added**

- **Jyotish Coach lab** (`examples/astro`), replacing the booking lab. It models two real incidents from a Vedic astrology coaching app (a "Synced" badge over rejected writes, and ages a day early behind UTC) plus a stale-coaching race. It includes:
  - a timing sweep (`examples.astro.sweep`);
  - a route-fidelity ablation (`examples.astro.ablation`);
  - failure messages that name the claim, the route, what was expected and observed, and where to repair.
- **Verification routes** (`docs/verify.md`): the smallest run that crosses every boundary a claim depends on, in seven fields.
- **Proof gaps guide** (`docs/proof-gaps.md`): a claim checklist, eight gap types and an audit. The checker enforces the proof matrix, with a new `environment` boundary.
- **Session check** (`harness_check.py --session`): changed files against the feature's scope, and claims against recorded evidence.
- **Transition gate** (`scripts/harness_transition.py`):
  - planner, worker and verifier roles, with an independent verifier required for `passing`;
  - a scope gate and a proof-plan gate before verification can be requested;
  - a hash-chained, append-only audit log, replayed on every check;
  - stale `passing` flagged when the verified code or claims change.
- **Session handoff** (`scripts/harness_handoff.py`): a checkpoint written from the observed repository, a handoff gate at the end of a session, and a Resume Protocol at the start. `AGENTS.md` and `CLAUDE.md` carry the protocol.
- **Adopt command** (`scripts/harness_adopt.py`): preview-first setup in any project that never overwrites existing files, with optional instruction files for Claude Code, Codex and Copilot, and an optional CI workflow.
- **Harness tests** (`harness-tests/`): 66 fixtures that run every gate against a named defect and against clean work. A failure code with no fixture fails the build. They run on every change and weekly.
- **Evaluation** (`evals/jyotish/`): the same user reports given to agents with and without the harness, judged by a hidden grader. It includes a 12-run pilot with Claude Haiku 4.5, Sonnet and Opus.
- **Annotated authority policy**, with a blank template and a table of what actually enforces each rule.

**Changed**

- A never-written checkpoint now means "no handoff yet" to `--resume`, instead of a stale handoff. The handoff gate still refuses it.
- Adopt prints the exact commit command for the files it created, so the first session check measures your work and not the setup.
- CI reports unit-test failures as annotations. Test repositories disable background git maintenance, which had caused intermittent cleanup failures on hosted runners.

## v0.1.0 (2026-09-27)

First public release: the read-only artifact checker, a model-free booking lab, starter templates for the five layers, and the handbook.
