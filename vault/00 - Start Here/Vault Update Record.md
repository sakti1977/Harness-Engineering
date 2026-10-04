---
type: verification-record
status: locally-verified
reviewed: 2026-09-28
---

# Vault Update Record

## What changed

The expansion adds source-backed notes on evaluation, grading, security boundaries, reproducible environments, context retrieval, tool usability, retries, budgets, memory, tracing and delegation. It adds a source register, repository pattern atlas, five reusable templates, three learning routes and a runnable synthetic booking lab.

Legacy source attribution remains intact. The clinic examples are explicitly instructional; unsupported numerical precision was removed. The five-layer model is labeled as this vault’s organizing synthesis. The original [[Harness knowledge base expansion|research report]] remains a dated proposal and audit snapshot; use this note and [[Harness Improvement Roadmap]] for subsequent implementation status.

## Executed local verification

Date: 2026-09-26. Environment: Linux, Python standard library; exact interpreter version is recorded in the repository’s verification record. No model calls or paid APIs were used.

- The artifact checker accepts the starter and rejects malformed JSON, invalid states, missing/empty artifacts, wrong field types, invalid paths and unsupported self-attested completion.
- Checker and documentation-tool regression tests run from the GitHub checkout with `python3 -m unittest discover -s tests -v`.
- All six fixed booking checks pass, including persistent state and simultaneous requests using separate SQLite connections.
- The demonstration’s weak check passes on broken code; exactly two outcome checks fail on that code; all fixed checks pass. The expected failures are part of the successful lab.
- Generated handbook parity, internal Markdown/wiki paths and equality of runnable lab copies are checked before publication. External source URLs and their claim support require separate human review.

## Scope limits and pending evidence

Only the booking fixture and repository checks have executable local results. Other exercises specify experiments for readers; they are not evidence that those security/runtime mechanisms have been implemented. No live-agent improvement, production sandbox, deployed API, multi-stack portability or external-user adoption is claimed.

The public repository contains the checker/tests/example and maintains this learning content in `vault/`, with generated navigation in `docs/handbook/`. A local Obsidian working copy must be synchronized before publishing; the export does not automatically synchronize two edited vaults.

## Next work

External pilot feedback, independently produced evidence receipts, a second stack, tested runtime adapters and live-agent experiments remain on [[Harness Improvement Roadmap]]. See [[Source Register]] for the evidence conventions.

## Update 2026-09-27

The booking lab is replaced by the Jyotish Coach lab in [[First Executable Harness Lab]], modelled on incidents recorded in [[Jyotish Coach Sync and Age Incidents]]. The repository adds written verification routes (`docs/verify.md`), an interleaving sweep, route-aware failure messages and a fidelity ablation. Executed locally on Python 3.10, 3.12 and 3.13: the lab demo, sweep, ablation and 70 repository tests passed; the threaded stale-coaching check was repeated 30 times per variant without an unexpected result. Other inherited clinic scenarios in this vault remain instructional examples.

## Update 2026-09-28

Twenty core notes were rewritten around this repository's executable examples and now carry `status: maintained` with a review date: the two foundation notes, the five layer maps, [[Claim-to-Proof Matrix]], [[Verification Routes and Test Fidelity]], [[Feature Ledger as a Gate]], [[Cold-Session Checkpoint]], [[Authority Policy]], [[Scope Contract]], [[Readiness Contract]], [[Recovery Audit]], [[AGENTS.md as a Map]], [[Harness-Control Tests]], [[Minimal Harness Adoption Path]], [[False Passing Feature]] and [[Cold Session Loses Diagnosis]]. Each follows problem, mechanism, worked example, try it, limits. Every "try it" command was run against a clean clone before publishing.

[[False Passing Feature]] now cites the evaluation pilot in `evals/jyotish/results/` as its measured counterpart; the pilot's limits (two runs per cell, Claude models only, one author) apply. Notes still marked `synthesized-from-shared-material` are inherited teaching summaries that have not yet been rewritten; treat them as orientation, not as a description of what this repository implements.

## Update 2026-10-04

The kit adds an executable attempt gate for the timeout case described in [[Retry and Idempotency Contract]]: `scripts/harness_attempt.py`, `docs/attempts.md` and `examples/gate/timeout_demo.py`. A timeout is recorded as an unknown outcome, the same key is refused until it is reconciled, and finished work is replayed instead of run again. Executed locally on Python 3.10, 3.12 and 3.13: 39 gate unit tests passed, and the harness-control tests now hold 84 entries (18 new, covering all ten gate codes plus clean cases). The demo simulates a lost response with a scripted agent: 4 suite executions and 4 records without the gate, 1 and 1 with it.

Scope limits: the agent is scripted, so no live-agent improvement is claimed. Time and tokens saved are not measured or priced. Windows and macOS CI runs were not executed here.
