# Local verification record

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
