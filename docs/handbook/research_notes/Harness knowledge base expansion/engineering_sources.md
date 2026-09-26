# Primary engineering sources for expanding the harness knowledge base

## Which sources provide useful evidence?

### Takeaway
Eight first-party engineering articles provide complementary practices. These are vendor engineering reports, not independent proof of general performance; dates below were read on the pages, accessed 2026-09-26.

### Cited Findings
- **S1 — OpenAI, Ryan Lopopolo, 2026-02-11.** Describes repository documentation checks, dependency-direction enforcement, isolated worktree applications with logs/metrics/traces, and recurring cleanup. It explicitly limits generalization beyond its invested-in repository. [Harness engineering](https://openai.com/index/harness-engineering/)
- **S2 — Anthropic, Justin Young, 2025-11-26.** Uses initializer and incremental coding sessions with persistent progress artifacts; compaction alone did not solve the demo's long-running failures. The experiment targets full-stack web applications. [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- **S3 — Anthropic, 2025-09-29.** Discusses selective context, lightweight references, runtime retrieval, and hybrid retrieval strategies; loading context on demand trades speed for relevance. [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- **S4 — Anthropic, 2025-09-11.** Recommends evaluating tool names, descriptions, schema clarity, output usefulness, and token efficiency against realistic tasks and held-out examples. [Writing effective tools](https://www.anthropic.com/engineering/writing-tools-for-agents)
- **S5 — Anthropic, 2026-01-09.** Separates evaluation tasks, trials, graders, traces, and outcomes. Recommends isolated environments, multiple trials, outcome checks, human calibration, and separate capability/regression suites. [Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- **S6 — Anthropic, Prithvi Rajasekaran, 2026-03-24.** Describes planner/generator/evaluator experiments, evaluator calibration, model-dependent scaffolding, and removing individual components to assess their value. Its qualitative app demonstrations do not establish universal multi-agent superiority. [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- **S7 — LangChain, Vivek Trivedy, 2026-02-17.** Reports Terminal-Bench 2.0 increasing from 52.8 to 66.5 while holding GPT-5.2-Codex fixed and changing its harness. Describes trace analysis, pre-completion verification, loop detection, and time budgeting. This is a vendor-reported benchmark result, not a prediction for this vault. [Improving Deep Agents](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)
- **S8 — LangChain, Vivek Trivedy, 2026-04-08.** Describes sourcing evaluations from production traces and curated tasks, category tagging, optimization/holdout splits, baseline runs, targeted changes, and human acceptance review. [Better Harness](https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals)

### Inferences
- The vault should teach how to measure and retire harness interventions, alongside how to implement them. This is a synthesis of S5–S8, not an established universal architecture.
- Keep each source's model, task domain, environment, and publication date next to its claim. Source authority supports provenance; it does not remove experimental limitations.

### Gaps
- This is a bounded primary-source review, not every trustworthy blog on the internet.
- No experiments were replicated. The benchmark lift above has not been independently validated here.
- Long-term maintainability and generalization to other domains remain unestablished by these articles.

## What already exists, and what should be expanded?

### Takeaway
The inspected vault already covers initialization, feature ledgers, repository maps, readiness, permission contracts, verification fidelity, compaction, journals, and failure packets. The clearest gaps are measurement, tool usability, operational observability, and maintaining the harness itself.

### Cited Findings
- Local [Source Coverage Index](../../00%20-%20Start%20Here/Source%20Coverage%20Index.md) maps 24 sections of previously shared material but gives no external bibliography. [AGENTS.md as a Map](../../02%20-%20Reach/AGENTS.md%20as%20a%20Map.md), [Readiness Contract](../../04%20-%20Ground/Readiness%20Contract.md), [Tool Extension Contract](../../09%20-%20Tools%20and%20Interfaces/Tool%20Extension%20Contract.md), [Verification Routes and Test Fidelity](../../06%20-%20Verdict/Verification%20Routes%20and%20Test%20Fidelity.md), [Harness-Control Tests](../../10%20-%20Harness%20Testing/Harness-Control%20Tests.md), and [Context Compaction Contract](../../07%20-%20Carry/Context%20Compaction%20Contract.md) were directly inspected.
- Initializer/progress-file ideas largely corroborate existing notes; use S2 to add attribution and a concrete external case, rather than another duplicate concept. [S2](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

### Inferences
The following are proposed vault changes, not claims that each practice always improves agents. P0 means foundation; P1 means useful next experiment.

1. **P0 — Add “Agent Evaluations and Harness Tests.”** Distinguish deterministic control tests from stochastic end-to-end evaluation. Include task, trial, grader, trace, and environment outcome. Link [Harness-Control Tests](../../10%20-%20Harness%20Testing/Harness-Control%20Tests.md). Exercise: show a successful transcript with a failed database outcome. [S5](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
2. **P0 — Add “Capability and Regression Suites.”** Explain when a difficult capability task becomes a regression case. Include repeated trials, pass@k versus pass^k, and reporting cost/latency beside success. Exercise: run one task repeatedly. [S5](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
3. **P0 — Add “Harness Experiment Log.”** Record baseline, hypothesis, one scoped intervention, behavior tags, optimization set, holdout results, regressions, and acceptance decision. Link [First Divergence and Failure Packet](../../06%20-%20Verdict/First%20Divergence%20and%20Failure%20Packet.md). [S8](https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals)
4. **P0 — Add “Tool Usability Evaluations.”** Extend [Tool Extension Contract](../../09%20-%20Tools%20and%20Interfaces/Tool%20Extension%20Contract.md) beyond dispatch correctness: measure wrong-tool selection, invalid parameters, redundant calls, output tokens, and successful outcomes on realistic tasks. [S4](https://www.anthropic.com/engineering/writing-tools-for-agents)
5. **P1 — Add “Tool Response Design.”** Compare full listing versus targeted search, clear namespaces, informative identifiers, and bounded responses. Exercise: redesign a noisy log tool and measure selection accuracy and token use. [S4](https://www.anthropic.com/engineering/writing-tools-for-agents)
6. **P0 — Add “Knowledge Base Maintenance.”** Extend [AGENTS.md as a Map](../../02%20-%20Reach/AGENTS.md%20as%20a%20Map.md) with owners, review dates, source links, stale-document checks, broken-link checks, and a small documentation-repair workflow. [S1](https://openai.com/index/harness-engineering/)
7. **P1 — Add “Architecture Rules as Executable Checks.”** Turn dependency boundaries and recurring review findings into structural checks with useful repair messages. Exercise: seed a forbidden import and verify rejection. [S1](https://openai.com/index/harness-engineering/)
8. **P1 — Add “Agent-Readable Observability.”** Teach isolated application instances, correlated logs/metrics/traces, reproducible UI evidence, and cleanup. Extend [Readiness Contract](../../04%20-%20Ground/Readiness%20Contract.md) with evidence that observations belong to the current run. [S1](https://openai.com/index/harness-engineering/)
9. **P1 — Expand “Repository Discovery Funnel” with retrieval tradeoffs.** Compare preloaded context, lightweight references plus on-demand reads, and hybrid retrieval. Exercise: measure missing facts, tokens, and discovery latency across the same tasks. [S3](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
10. **P1 — Expand “Context Compaction Contract” with strategy selection.** Contrast in-place compaction, durable notes, and clean-context handoff. Test retained decisions and resumption accuracy rather than assuming a larger window solves context problems. [S3](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); [S6](https://www.anthropic.com/engineering/harness-design-long-running-apps)
11. **P1 — Add “Independent Evaluation and Rubric Calibration.”** Compare self-review with a separate evaluator, inspect disagreements with humans, and test actual application behavior. Explain that evaluator separation alone does not remove leniency. [S6](https://www.anthropic.com/engineering/harness-design-long-running-apps)
12. **P1 — Add “Model Upgrade and Harness Ablation.”** Remove one intervention at a time and rerun the same tasks when models change. Retire unnecessary orchestration only when measured outcomes hold. [S6](https://www.anthropic.com/engineering/harness-design-long-running-apps)
13. **P1 — Add “Loop Detection and Recovery.”** Detect repeated edits or repeated failures; inject a reconsideration step and preserve a trace. Evaluate false alarms and successful escapes. A reminder is a heuristic, not guaranteed recovery. [S7](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)
14. **P1 — Add “Budgets and Completion Checks.”** Reserve time for verification, make remaining budget visible, and test a pre-completion checklist. Compare completed verified tasks per unit cost rather than maximum reasoning on every step. [S7](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)
15. **P0 — Add “Failure-to-Evaluation Workflow.”** Convert recurring failure packets into small tagged cases, preserve held-out examples, and record why a proposed change was accepted or rejected. Exercise: turn an existing case study into an evaluation specification. [S8](https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals)

### Gaps
- No runnable agent code or evaluation corpus was evaluated in this assigned review, so these are knowledge-base enhancements and experiment designs, not verified runtime fixes.
- Local coverage assessment used the complete file listing and selected concept notes, not a claim of line-by-line review of every note.

## How should claims and disagreements be presented?

### Takeaway
Use conditional guidance and preserve differences between task types, model versions, and evidence strength. Separate observed vendor results from proposed local experiments.

### Cited Findings
- A small incremental coding workflow was useful in the earlier long-running demo; later experiments question which scaffolding remains necessary as models improve. These are evolving observations rather than a timeless rule to always use one feature per session. [S2](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents); [S6](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- Outcome-oriented evaluation accepts valid alternative paths; tests that require exact call sequences can reject correct solutions. Policy or safety constraints can still need their own deterministic checks. [S5](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- Optimization can improve aggregate scores while introducing regressions, which motivates inspecting categories and held-out cases rather than a single headline score. [S8](https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals)

### Inferences
- Suggested source-note fields: title, author, organization, URL, publication date, accessed date, evidence type, task/model scope, claims used, limitations, and linked concepts.
- Suggested concept-note fields: problem, mechanism, when useful, when harmful, minimal example, failure injection, success measure, sources, and related concepts.
- Keep architectural rules separate from model-behavior heuristics: one enforces intended boundaries; the other should be periodically re-evaluated.

### Gaps
- The sources do not establish a universal best harness, universal number of agents, universal context size, or guaranteed productivity gain.
- Vendor examples should not be transformed into claims that autonomous merging, relaxed gates, or additional evaluators are appropriate for every project.
