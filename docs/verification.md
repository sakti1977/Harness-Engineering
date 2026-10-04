# Local verification record

## 2026-10-04: attempt gate (unreleased)

Host: Linux. Interpreters: Python 3.10, 3.11, 3.12 and 3.13. No model calls, paid APIs or third-party packages. Windows and macOS were not run locally; hosted CI for them is unverified for this change.

- `python3 -m unittest discover -s tests`: 142 tests passed on each interpreter, 39 of them for the attempt gate.
- `python3 harness-tests/run.py`: 84 entries, 0 problems (18 new `attempt` entries covering all ten codes, plus five clean cases).
- `python3 -m examples.gate.timeout_demo`: `TIMEOUT DEMO PASSED`. In the simulation, 4 suite executions and 4 records without the gate; 1 and 1 with it, with a probe or with an operator decision.
- Lab demo, gate demo, sweep and ablation: all report PASSED. Handbook export: 95 files verified. Documentation checks: 0 issues.
- The agent in the demo is scripted. Time and tokens saved are not measured, and no live-agent improvement is claimed.

## 2026-09-28: portability and handbook update (unreleased)

Host: Linux. Interpreters: Python 3.10, 3.12 and 3.13. Hosted CI: Linux (3.10, 3.12, 3.13), macOS and Windows (3.12). No model calls, paid APIs or third-party packages.

- `python3 -m unittest discover -s tests -v`: 102 tests passed on each local interpreter (three new adopt tests).
- `python3 harness-tests/run.py`: 66 entries, 0 problems on each interpreter.
- Lab demo, gate demo, sweep and ablation: all report PASSED. Handbook export: 95 files verified. Documentation checks: 0 issues.
- The first macOS and Windows CI runs failed: 15 handoff and resume fixtures were refused with `artifact resolves outside project`, two `.git` removals hit read-only files on Windows, and one eval test compared a short Windows path with a resolved one. The first failure was reproduced on Linux by pointing `TMPDIR` at a symlink (15 problems before the fix, 0 after). After the fixes, every job in the hosted matrix passed.
- Every "try it" command in the twenty rewritten handbook notes was run against a clean clone; three that did not behave as first written were corrected before publishing.

## 2026-09-28: v0.2.0 release candidate

Host: Linux. Interpreters: Python 3.10, 3.12 and 3.13. No model calls, paid APIs or third-party packages.

- `python3 -m unittest discover -s tests -v`: 99 tests passed on each interpreter.
- `python3 harness-tests/run.py`: 66 entries, 0 problems on each interpreter (every failure code covered; every gate has a clean fixture).
- `python3 scripts/harness_check.py --adapter copilot`: passed. `python3 scripts/harness_handoff.py --resume` on a fresh clone: passes with "no handoff has been written yet".
- Lab demo, gate demo, sweep and ablation: all report PASSED. Handbook export: 95 files verified. Documentation checks: 0 issues.
- Every command in the README was run from a fresh clone of `main` before this release candidate; the adopt-then-session-check friction found there is fixed in this release.
- `evals/jyotish`: the grader self-check (`tests/test_eval_jyotish.py`) passes; the published pilot results were regenerated with the committed `grade.py` and `regression.py`.

## 2026-09-27: Jyotish Coach lab

Host: Linux. Interpreters: Python 3.10, 3.12 and 3.13 (default 3.11.15). No model calls, paid APIs or third-party packages.

- `python3 -m unittest discover -s tests -v`: 70 tests passed on each interpreter (checker, session, transitions, proof matrix, lab tools, documentation tools).
- `python3 -m unittest examples.astro.test_astro -v`: all 7 lab checks passed on the fixed app.
- `python3 -m examples.astro.demo`: three weak checks green on the broken app; exactly the three intended outcome claims failed; all outcome checks green on the fixed app; `LAB PASSED`.
- `python3 -m examples.astro.sweep`: the broken app stored stale coaching at 11 of 13 injection points (not at the first or last); the fixed app at none; `SWEEP PASSED`.
- `python3 -m examples.astro.ablation`: the faithful route and two single-check weakenings discriminate; sequential runs are always red until the expectation is edited, which then false-passes, as do per-actor stores and weakening both checks; `ABLATION PASSED`.
- `python3 -m examples.gate.demo`: `GATE DEMO PASSED`.
- The threaded stale-coaching test was repeated 30 times on each variant with no unexpected result.
- Handbook export and documentation checks: 95 files verified, 0 issues.

The lab replaces the earlier booking example. The record below is the original release's verification and is kept unchanged.

## 2026-09-26: first release

Date: 2026-09-26. Host: Linux. Interpreter: Python 3.12.3. No model calls, paid APIs or third-party Python packages were used.

## Results

- `python3 scripts/harness_check.py --adapter copilot`: passed; artifact and feature-schema scope only.
- `python3 -m unittest discover -s tests -v`: 12 tests passed, covering checker rejection paths, read-only CLI behavior, link export and missing-link detection.
- `python3 -m unittest examples.booking.test_booking -v`: all 6 fixed-application tests passed.
- `python3 -m examples.booking.demo`: weak check green on broken code; exactly 2 intended outcome failures; all fixed tests green; exit 0 and `LAB PASSED`.
- `python3 scripts/export_handbook.py --check`: generated handbook matches the canonical vault.
- `python3 scripts/check_docs.py`: local links resolve and runnable lab copies match.

The demo's expected middle failures are evidence that the checks detect the seeded defect. They are not unexplained test failures. Tests use temporary local databases with explicit connection cleanup.

## Interpretation

These checks establish the behavior of the included artifact validator, documentation tooling and synthetic booking example. They do not establish production readiness, remote HTTP behavior, a secure sandbox, live-agent performance or successful external-user adoption.

The workflow also runs Python 3.10, 3.12 and 3.13 on GitHub-hosted Linux. Its actual run status is available under the repository's Actions tab; local verification alone does not prove the hosted matrix passed. External links and whether sources support claims require separate review; the documentation checker is offline.
