# Roadmap and release boundaries

## Implemented in this update

- Accurate checker scope, strict feature validation, negative tests and JSON findings.
- Optional vendor instruction check; core validation is tool-neutral.
- Runnable synthetic lab, including persisted state and concurrent requests (since replaced by the Jyotish Coach lab).
- MIT code/documentation license, contribution guidance, issue forms and CI configuration.
- Expanded Obsidian learning content and generated GitHub navigation from the same source.

## Implemented after the first release

- Session mode: changed files against `expected_surface` and `excluded_paths`, claims against recorded evidence.
- Feature transition policy with planner, worker and verifier roles, an independence rule for `passing`, a hash-chained append-only audit log, and automatic staleness when verified code or claims change.
- Jyotish Coach lab modelled on real incidents (sync badge, age behind UTC) plus a stale-coaching race, with written verification routes, an interleaving sweep, route-aware failure messages and a fidelity ablation.
- Proof-matrix coverage: every claim needs a producer tested at its required boundary before verification can be requested, with a proof-gap audit guide.

## Next acceptance gates

- Observe at least three unfamiliar users complete the lab without maintainer assistance; record friction.
- Let CI record evidence and `passing` transitions directly, so no human or agent writes them by hand.
- Support several features per ledger, with dependencies.
- Add a preview-first installer that preserves existing project files, only if manual adoption is a demonstrated barrier.
- Add a second stack and adapters only with explicit platform coverage and maintained fixtures.
- Run live-agent baseline/variant trials with a calibrated grader, recorded cost and held-out tasks.
- Publish independent case studies, a support policy and measured adoption outcomes.

These are pending. This release does not claim universal project diagnosis, production security or improved model performance. Stars and clones are discovery signals; successful independent use is the first product milestone.

See [the detailed research roadmap](handbook/00%20-%20Start%20Here/Harness%20Improvement%20Roadmap.md).
