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
- Adopt command: preview-first setup of the contracts, agent instructions and an optional CI workflow in any project, never overwriting existing files.
- Evaluation: the Jyotish user reports given to agents with and without the harness, with a hidden grader, a regression check and a 12-run Claude pilot.
- Session handoff: a checkpoint written from the observed repository, a handoff gate for the end of a session and a Resume Protocol that treats stale checkpoints as failed checks.
- Harness tests: every gate runs against a defect fixture and a clean fixture on each change and weekly; uncovered failure codes fail the build.

## Next acceptance gates

- Observe at least three unfamiliar users complete the lab and the adopt path on their own projects without maintainer assistance; record friction.
- Let CI record evidence and `passing` transitions directly, so no human or agent writes them by hand.
- Support several features per ledger, with dependencies.
- Add a second stack and adapters only with explicit platform coverage and maintained fixtures.
- Extend the evaluation: other vendors' agents, at least five runs per cell, an ablation separating claims and routes from gates, and held-out tasks by other authors.
- Publish independent case studies, a support policy and measured adoption outcomes.

These are pending. This release does not claim universal project diagnosis, production security or improved model performance. Stars and clones are discovery signals; successful independent use is the first product milestone.

See [the detailed research roadmap](handbook/00%20-%20Start%20Here/Harness%20Improvement%20Roadmap.md).
