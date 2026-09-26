# sakti1977/Harness-Engineering: verified audit and adoption plan

## What is actually in the repository?

### Takeaway
The repository is a small, readable instructional scaffold with a deterministic artifact checker. Its current implementation does not yet enforce the authority, scope, readiness, or evidence policies described in its documents. Build a trustworthy diagnostic-and-adoption product around this foundation before broad promotion.

### Cited Findings
Inspection date: 2026-09-26. GitHub web retrieval failed, but the connected GitHub API succeeded. All nine files in the complete, nontruncated default-branch tree were read. Snapshot commit: `a800a594297451eab10e6ff0c9cde94a3e31aca0`. [Commit](https://github.com/sakti1977/Harness-Engineering/commit/a800a594297451eab10e6ff0c9cde94a3e31aca0); [complete tree API](https://api.github.com/repos/sakti1977/Harness-Engineering/git/trees/main?recursive=1)

- Public repository, default branch `main`, created September 22, 2026; most recent push September 22. At inspection: 0 stars, 0 forks, no topics, homepage, Pages site, or Discussions; API license field is null. These are a dated snapshot, not evidence of future potential. [Repository API](https://api.github.com/repos/sakti1977/Harness-Engineering)
- README introduces the Reach/Power/Ground/Verdict/Carry model, one sample check command, and a suggested adoption order. It starts adoption by copying Copilot instructions, but lacks a complete worked installation into another project. [README](https://github.com/sakti1977/Harness-Engineering/blob/a800a594297451eab10e6ff0c9cde94a3e31aca0/README.md)
- Root tree contains `.github/copilot-instructions.md`, two `.harness` examples, four policy documents, README, and the checker. There are no tests, executable booking example, package metadata, workflows, license file, contribution/security documents, or issue templates in this snapshot. [Tree](https://api.github.com/repos/sakti1977/Harness-Engineering/git/trees/a800a594297451eab10e6ff0c9cde94a3e31aca0?recursive=1)
- The feature example refers to `src/booking.py`, `tests/test_booking.py`, and a pytest verification command; these paths are absent from the tree. It is illustrative, not a runnable booking demonstration. [Feature example](https://github.com/sakti1977/Harness-Engineering/blob/a800a594297451eab10e6ff0c9cde94a3e31aca0/.harness/feature.json); [tree](https://api.github.com/repos/sakti1977/Harness-Engineering/git/trees/main?recursive=1)
- The authority document lists meaningful prohibitions and refusal codes, but no runtime permission interceptor is present. Copilot instructions describe desirable behavior; these files cannot themselves provide OS or tool-level enforcement. [Authority](https://github.com/sakti1977/Harness-Engineering/blob/a800a594297451eab10e6ff0c9cde94a3e31aca0/docs/authority.md); [instructions](https://github.com/sakti1977/Harness-Engineering/blob/a800a594297451eab10e6ff0c9cde94a3e31aca0/.github/copilot-instructions.md)
- The checker uses `Path.exists`, checks required JSON keys, rejects the exact state `passing`, and otherwise prints `HARNESS READY`. It does not execute readiness probes, verify evidence, validate field types/contents, restrict state values, or inspect changed-file scope. Malformed JSON is not caught. These are static code findings, not executed tests. [Checker](https://github.com/sakti1977/Harness-Engineering/blob/a800a594297451eab10e6ff0c9cde94a3e31aca0/scripts/harness_check.py)
- No workflow runs, releases, or issues were returned. [Actions API](https://api.github.com/repos/sakti1977/Harness-Engineering/actions/runs?per_page=3); [releases API](https://api.github.com/repos/sakti1977/Harness-Engineering/releases); [issues API](https://api.github.com/repos/sakti1977/Harness-Engineering/issues?state=all&per_page=10)
- Local Obsidian workspace is not a Git checkout (`git remote -v` returned “not a git repository”). Its expanded notes and the remote scaffold are distinct artifacts; no synchronization was assumed or performed.

### Inferences
**Priority defects and product gaps:**

1. The readiness label overstates the checker’s verified scope. Change success wording to artifact/schema validation and reserve readiness for executed probes.
2. Add robust parsing, object/schema/type validation, state enums, nonempty required values, actionable failure messages, and stable exit codes.
3. Replace hard-coded Copilot-file requirements with a vendor-neutral core plus explicitly selected adapter requirements.
4. Separate an illustrative feature from the adopter’s actual active feature. Ship a runnable booking fixture matching the documented claims.
5. Connect completed-feature status to independently generated evidence bound to revision, command, result, and required claims; do not merely ban completion forever.
6. Present guidance, local checking, and runtime enforcement as distinct capability levels in documentation and CLI output.

### Gaps
No code was executed in this assigned audit; no remote settings or content were changed. Branch protection, private traffic/clone statistics, and repository security settings were not inspected. License intent is unknown; choosing terms belongs to the owner, and this plan makes no legal conclusion.

## What product and knowledge architecture should be built?

### Takeaway
Position the project as a practical way to diagnose, adopt, and measure harness controls in an existing codebase. Let the vault explain the reasoning and failure modes while the GitHub repository supplies tested templates, adapters, examples, and checks.

### Cited Findings
- Structured repository knowledge and mechanical documentation checks are described in OpenAI’s engineering account. [OpenAI](https://openai.com/index/harness-engineering/)
- Anthropic distinguishes reproducible control checks from evaluating model-plus-harness behavior, with isolated trials and calibrated graders. [Anthropic evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- LangChain’s improvement process combines baseline runs, targeted changes, tagged failure cases, holdouts, and acceptance review. [LangChain Better Harness](https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals)

### Inferences
All following structures, commands, schedules, and targets are proposals, not existing features or guaranteed outcomes.

**User journey:** inspect a project → get prioritized evidence-backed gaps → choose a small control → preview changes → apply templates → run a failure demonstration → verify improvement → maintain the control.

**Three entry routes:**

- Learn: a short conceptual path and progressive labs, usable without model credentials.
- Adopt: a guided existing-project route with dry-run changes, backups, merge/conflict handling, and rollback.
- Tune: baseline/variant comparisons with pinned model, harness, task and environment versions, costs, traces, and held-out cases.

**Suggested repository shape:**

```text
README.md
LICENSE / CONTRIBUTING.md / SECURITY.md / CODE_OF_CONDUCT.md
docs/                    # rendered handbook; navigation and sources
vault/                   # portable Obsidian learning view, generated or canonical
src/                     # small diagnostic and validation implementation
schemas/                 # versioned feature, evidence, checkpoint, config schemas
templates/core/          # portable contracts
adapters/                # Copilot, Codex, Claude Code, etc.; declared test coverage
examples/booking/        # runnable healthy and deliberately broken cases
examples/project-types/  # later: Python API, JS/TS app, monorepo
tests/fixtures/          # clean, malformed, missing, stale, denied, cancelled cases
evals/                   # optional live-agent tasks and experiment manifests
.github/workflows/       # test, docs, artifact, release checks
```

Choose one canonical Markdown source for handbook and vault. Generate alternate navigation/links; avoid maintaining two divergent bodies. Keep source metadata and concept IDs stable. CI should check broken wiki links, orphan concepts, missing evidence links, schemas, and exported Markdown navigation. Obsidian-specific conveniences should be optional.

**Knowledge note standard:** problem; concrete failure; mechanism; minimal implementation; when it helps; when it adds cost; deterministic test; optional agent experiment; sources and dates; evidence strength; related concepts. Add skill-level prerequisites, time estimates, and worked lab results.

**Possible future command design:** `harness doctor --path PROJECT` (read-only); `harness init --dry-run`; `harness check --format json`; `harness verify`; `harness report`. Do not document these as runnable until implemented. Diagnosis must distinguish “missing,” “configured,” “tested,” and “enforced”; a numeric maturity score alone must not imply safety or reliability.

**Differentiator:** every recommendation links a failure example, a small installable control, a seeded test proving detection, an evidence limitation, and a maintenance cost. This is more useful than a large undifferentiated list of agent tools.

### Gaps
The best initial supported stack and preferred packaging ecosystem require maintainer prioritization. Start with the existing Python implementation and one additional project type only after user testing. Avoid promising compatibility with every coding agent until adapter behavior is verified.

## What sequence could earn sustained adoption?

### Takeaway
Aim first for successful independent adoption and demonstrated usefulness. Thousands of stars and clones are ambitions that cannot be promised; release quality, clear examples, and contributor experience are controllable.

### Cited Findings
The present repository has no release or workflow history and a very small footprint; an incremental release plan fits the verified starting point. [Releases](https://api.github.com/repos/sakti1977/Harness-Engineering/releases); [Actions](https://api.github.com/repos/sakti1977/Harness-Engineering/actions/runs?per_page=3); [tree](https://api.github.com/repos/sakti1977/Harness-Engineering/git/trees/main?recursive=1)

### Inferences
**Phase 0 — Honest foundation (first week; planning estimate).**

- Fix readiness wording and validator robustness; add schema tests with clean and seeded-defect fixtures.
- Choose license, add support/contribution/security guidance and source attribution.
- Add CI that tests actual commands and docs links; publish a scoped v0.1 release.
- Rewrite README around who benefits, a two-minute demonstration, prerequisites, supported capability boundaries, and three entry routes.
- Exit gate: a fresh clone runs a model-free example and correctly rejects malformed, missing, and invalid artifacts; every claim in README has executable or documentary evidence.

**Phase 1 — First practical adoption (weeks 2–3; estimate).**

- Add read-only diagnosis, dry-run initialization, configuration, and portable templates.
- Deliver complete booking example: show a false pass, reproduce the defect, add the relevant control, produce evidence.
- Pilot with five external users on repositories unfamiliar to the maintainer. Observe setup without intervening; record failure points.
- Exit gate: at least four of five pilots reach their first useful finding/control unaided within a proposed 15-minute target; no existing project files are silently overwritten.

**Phase 2 — Evidence and breadth (weeks 4–6; estimate).**

- Add a second stack, tested agent adapters, checkpoints, revision-bound verification evidence, and versioned migration guidance.
- Publish small baseline/variant experiments with failures as well as wins. Keep deterministic tests separate from optional paid live-agent evaluations.
- Build the Obsidian learning path: beginner labs, practitioner recipes, advanced experimentation; make the handbook searchable and usable on GitHub/web.
- Exit gate: two stacks have reproducible examples; new adopters can select a control from a symptom and understand its limits; benchmark reports disclose cost and repeated-trial variation.

**Phase 3 — Contributor and community release (weeks 7–10; estimate).**

- Add issue forms for adoption problems, reproducible failures, adapters, and evidence corrections.
- Curate small good-first-issues with acceptance tests; define review response expectations and adapter maintenance ownership.
- Publish a short demo, a detailed failure-to-fix article, and real adopter case studies with permission. Offer upstream improvements to relevant projects; announce only in communities where the material is useful and posting rules permit it.
- Ask for stars after users have obtained value; avoid star swaps, artificial activity, or claims that stars prove technical quality.
- Exit gate: three independently authored case studies or substantial contributions; maintainers can triage and review without the project depending on one person’s unwritten knowledge.

**Phase 4 — Sustain (ongoing).**

- Time-box source freshness review and model/adapter revalidation; publish support and deprecation policy.
- Maintain a public roadmap driven by recurring adoption failures, not feature count.
- Expand languages only with terminology ownership and translation freshness checks; expand frameworks when demand and maintainers exist.

**Measurement:** track time to first useful result, independent quickstart completion, repeated use, detected real failures, false alarms, successful upgrades, contributor retention, issue response time, release reliability, and documented adoption. Track stars/forks as discoverability signals. Clone counts require authorized owner analytics; do not infer them from stars, and do not conflate a clone with a retained user. The suggested pilot targets are internal goals, not evidence-backed growth forecasts.

**First implementation backlog, in order:** truthful checker output → schema validation and fixtures → CI → runnable booking lab → README and license → source-backed handbook/vault publishing → read-only doctor → dry-run adoption → evidence records → tested adapters → pilot fixes → public case studies.

### Gaps
No distribution, growth, or adoption experiments have been run. Timeline estimates assume focused maintainer availability and should be revised after Phase 1. This plan does not guarantee popularity, and no external messages, settings changes, releases, or remote writes were performed.
