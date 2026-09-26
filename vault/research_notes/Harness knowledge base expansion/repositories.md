# Official repository research for harness engineering

## Which repository patterns add useful depth to this vault?

### Takeaway
The vault already covers the agent loop, authority, journals, checkpoints, tool contracts and deterministic control tests. Its strongest next step is a set of worked implementation comparisons and executable exercises, with explicit version and failure semantics. This assessment follows inspection of the local README, Source Coverage Index, Agent Loop and Provider Seam, Harness-Control Tests, and the complete Markdown filename inventory.

### Cited Findings
- **Minimal baseline:** mini-swe-agent separates agent, environment, model and runner; its documented design uses shell actions, independent subprocess execution and a linear message history. The README distinguishes this baseline from SWE-agent's richer tool/history experiments. — [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)
- **Version and maintenance status:** mini-swe-agent's current README identifies v2 and points to a migration guide. SWE-agent says most development has moved to mini-swe-agent and recommends it for new use. This makes SWE-agent valuable as an interface-design comparison, rather than an unqualified default. — [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent); [SWE-agent](https://github.com/SWE-agent/SWE-agent)
- **Measured limits:** the minimal agent implementation checks step, cost and wall-time limits. Cost is accumulated after a model call; the configuration explicitly describes the cost threshold as a limit that may be exceeded. State is saved in a `finally` block. — [default.py](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/agents/default.py)
- **Enforcement differs by platform:** Codex core documents writable-root protection, platform backends, policy compatibility constraints and fail-closed behavior for unsupported Windows policies. It also distinguishes host, target and remote test conditions. — [Codex core README](https://github.com/openai/codex/blob/main/codex-rs/core/README.md)
- **Hooks as an example, not complete containment:** Anthropic's hello-world demo uses a pre-tool hook to constrain JavaScript/TypeScript writes for selected editor tools, and exposes turn and allowed-tool options. — [Hello World](https://github.com/anthropics/claude-agent-sdk-demos/blob/main/hello-world/README.md)
- **Delegation provenance:** the research-agent demo persists Markdown findings and structured tool logs; hooks record agent, time, inputs/outputs, and link child calls through `parent_tool_use_id`. — [Research Agent](https://github.com/anthropics/claude-agent-sdk-demos/blob/main/research-agent/README.md)
- **Demo limitations:** Anthropic labels the SDK examples local-development demonstrations. The chat demo identifies authentication, persistent chat storage, transcript synchronization and SDK isolation as production work. — [Demo repository](https://github.com/anthropics/claude-agent-sdk-demos); [Chat demo](https://github.com/anthropics/claude-agent-sdk-demos/blob/main/simple-chatapp/README.md)
- **Execution/deployment boundary:** OpenHands SDK separates agent/conversation/workspace execution from UI and automation ownership. Its examples cover standalone SDK, remote server, GitHub workflows and skills/plugins. It supports local or ephemeral workspaces. — [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk)
- **Memory has separate scopes:** LangGraph distinguishes thread checkpoints from application data stores shared across threads. In-memory checkpoints vanish at restart; its documentation also discusses checkpoint retention. — [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence); [LangGraph repository](https://github.com/langchain-ai/langgraph)
- **A protocol acknowledgment is not completion:** the Codex app-server documents cancellation acknowledgment separately from the eventual RPC result; cancellation cannot undo completed effects. Stored attachments have an identity-based idempotency contract. — [App-server README](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)
- **Evaluation provenance matters:** SWE-bench uses Docker for reproducible patch evaluation. Its README warns that results are cached by run and instance IDs, even if a patch changes, and requires a new run ID for re-evaluation. — [SWE-bench](https://github.com/SWE-bench/SWE-bench)
- **A public product repository is not automatically a complete runtime implementation:** Claude Code's repository documents installation, issue reporting and bundled plugins. Use the SDK demo repository for explicit worked integration examples. — [Claude Code](https://github.com/anthropics/claude-code)

### Inferences
The following are proposed vault improvements, not measured outcomes or claims made by the repositories.

1. **Add a minimal baseline lab.** Extend `11 - Practical Implementations/Minimal Harness Adoption Path.md` with a small local issue fixture using the mini-swe-agent architecture. Record model, prompt, environment, budget, patch and trajectory. Compare each added mechanism against that baseline. Success criterion: another reader can reproduce the fixture and explain every state transition. Limit: a shell-only baseline still requires containment and authorization.
2. **Add tool-interface ablations.** Create `10 - Harness Testing/Tool Interface Experiments.md`: compare shell-only access with structured search/edit tools on the same tasks and fixed model settings. Measure invalid actions, recovery steps, latency, cost and successful patches. Link `Tool Extension Contract` and `Repository Discovery Funnel`. SWE-agent provides the richer historical comparator. Avoid concluding that either design wins universally from repository claims.
3. **Add a budget ledger and stop-reason exercise.** Extend `Agent Loop and Provider Seam` with explicit step, elapsed-time and monetary ledgers; preserve exhausted-budget status in the journal. Inject malformed billed responses and failures during save. Distinguish a pre-call budget check from a hard spending cap; estimate and reserve worst-case next-call cost when a hard ceiling is needed. Link mini-swe-agent `default.py` as a readable implementation.
4. **Turn authority policy into a platform matrix.** Add `03 - Power/Sandbox Enforcement Matrix.md` covering read/write roots, network access, subprocesses, protected control files and unsupported policies. Include host-versus-target test distinctions from Codex core. Exercise nested roots and forbidden writes in disposable fixtures. Success means denied effects do not occur; instructions alone do not establish containment.
5. **Add a hook coverage lab.** Link the Claude hello-world example from `Authority Policy` and `Harness-Control Tests`. Document exactly which tools a hook intercepts. A proposed test should attempt the same forbidden write through both an editor tool and a shell in a disposable sandbox, then show which layer denies each route. The published example is inspiration, not evidence of complete security coverage.
6. **Add multi-agent ownership and trace structure.** Create `08 - Agent Runtime/Delegation Contracts and Trace Lineage.md`: bounded task, owned output paths, parent/child IDs, status, artifact links and acceptance criteria. Adapt the research demo's trace lineage. Exercise a child failure and conflicting outputs. Connect `Concurrent Edit Clobber` and `First Divergence and Failure Packet`; add logs without assuming logs themselves prevent conflicts.
7. **Separate checkpoints, knowledge and retention.** Extend `Cold-Session Checkpoint` and add `07 - Carry/Memory Scope and Retention.md`. Distinguish live conversation state, resumable checkpoints, durable user/project knowledge and source evidence. Use LangGraph's two scopes as a concrete example. Test restart, cross-thread isolation and stale memory removal; persistence does not imply that remembered content is correct.
8. **Add cancellation and idempotency protocol cases.** Extend `TUI Controls and Cancellation` with requested/acknowledged/completed states, late-result handling and already-completed effects. Add `12 - Case Studies/Cancellation Acknowledged After Side Effect.md`. Use Codex app-server contracts to motivate a scripted race test. Generalize the identity-key approach for repeatable artifact attachment; do not promise exactly-once execution for arbitrary external tools.
9. **Add deployment boundary and readiness recipes.** Create `11 - Practical Implementations/From Local Demo to Hosted Harness.md`. Compare standalone OpenHands workspace, remote agent server and UI, then enumerate authentication, transcript storage, sandbox lifecycle, credentials and tenant separation using the Anthropic chat demo's admitted gaps. Add restart and isolation verification steps. Keep vendor-specific API snippets pinned to a release.
10. **Add a reproducible evaluation pack.** Extend `Verification Routes and Test Fidelity` with task version, repository commit, image identity, patch hash, model/config, run ID and raw logs. Use SWE-bench for a worked patch-evaluation example and retain deterministic control tests separately. Demonstrate how reused cache IDs can preserve stale results. Start with one task: the repository documents substantial resource needs for broader evaluation.

### Gaps
- No upstream code was executed, dependencies installed, benchmark scores independently reproduced, or security boundaries audited in this research pass.
- Current `main` pages were inspected, not immutable commit snapshots. Before turning examples into maintained runnable labs, resolve and record exact commit SHAs or release tags, dependency versions and image digests.
- Proposed paths above are additions or extensions; only this research note has been created by this researcher.
- The existing vault is concise and source coverage currently maps to shared conversation material. Claims about complete absence of a topic should remain qualified until every note's body is reviewed.

## Which sources should enter the source register?

### Takeaway
Use first-party code and documentation as implementation evidence. Retain repository maintenance status and version constraints alongside each source, and separate maintainers' benchmark claims from independently reproduced measurements.

### Cited Findings
All links below were opened during research on 2026-09-26. Access date is not publication date. URLs target moving branches unless stated otherwise.

- **R1 — OpenAI / Codex core.** Primary implementation documentation; platform enforcement and test-target semantics. [Source](https://github.com/openai/codex/blob/main/codex-rs/core/README.md)
- **R2 — OpenAI / Codex app-server.** Primary protocol documentation; cancellation, external effects and idempotent artifact identities. [Source](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)
- **R3 — SWE-agent team / mini-swe-agent.** Primary README; minimal architecture and v2 migration context. [Source](https://github.com/SWE-agent/mini-swe-agent)
- **R4 — SWE-agent team / default agent implementation.** Primary source code; limits and save path. [Source](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/agents/default.py)
- **R5 — SWE-agent team / SWE-agent.** Primary README; richer configurable interface experiments and supersession notice. [Source](https://github.com/SWE-agent/SWE-agent)
- **R6 — Anthropic / Claude Agent SDK demos.** Primary examples, explicitly not production deployments. [Repository](https://github.com/anthropics/claude-agent-sdk-demos), [hook example](https://github.com/anthropics/claude-agent-sdk-demos/blob/main/hello-world/README.md), [delegation example](https://github.com/anthropics/claude-agent-sdk-demos/blob/main/research-agent/README.md), [deployment gaps](https://github.com/anthropics/claude-agent-sdk-demos/blob/main/simple-chatapp/README.md)
- **R7 — OpenHands / Software Agent SDK.** Primary README; workspace/server and subsystem ownership. [Source](https://github.com/OpenHands/software-agent-sdk)
- **R8 — LangChain / LangGraph.** Primary repository and vendor documentation; thread state and cross-thread stores. [Repository](https://github.com/langchain-ai/langgraph), [persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- **R9 — SWE-bench maintainers / SWE-bench.** Primary evaluation implementation and usage; reproducibility and cache limits. [Source](https://github.com/SWE-bench/SWE-bench)
- **R10 — Anthropic / Claude Code.** Primary product-facing repository, plugin and issue entry point. [Source](https://github.com/anthropics/claude-code)

### Inferences
- Recommended source-card metadata: owner, URL, document kind, retrieved date, commit/tag, inspected file path, supported claims, caveats, linked vault notes and next review date.
- The most useful first three labs are the baseline, hook coverage and evaluation-provenance examples. They directly deepen existing notes while making claims testable.

### Gaps
- This is a deliberately bounded selection of major first-party repositories, not an exhaustive catalogue of every harness or trusted source.
- No fixed upgrade cadence or source automation was installed. Version pinning and refresh remain explicit follow-up work.

## Which credible repositories meet the user's thousand-star filter?

### Takeaway
The following 13 repositories meet an interpreted threshold of at least 1,000 visible GitHub stars. Counts are GitHub's rounded display observed on 2026-09-26, not exact API counts. Popularity is a discovery filter; owner provenance, inspectable implementation, documentation and maintenance status determine usefulness. This is a broad curated set, not a claim to exhaust GitHub.

### Cited Findings

| Repository | Observed stars | What to study for this vault |
|---|---:|---|
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | 148.1k | Product-facing plugin examples and issue history; do not mistake it for a full runtime source release |
| [openai/codex](https://github.com/openai/codex) | 126.5k | Agent runtime, sandbox policy and app-server contracts |
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | 89.2k | Application boundary, UI, automation and SDK relationship |
| [microsoft/autogen](https://github.com/microsoft/autogen) | 61.2k | Layered multi-agent design; explicitly maintenance mode, so use as historical/comparative material |
| [Aider-AI/aider](https://github.com/Aider-AI/aider) | 49.2k | Repository maps, Git change tracking and lint/test feedback |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 42.3k | Stateful orchestration and persistence |
| [huggingface/smolagents](https://github.com/huggingface/smolagents) | 29.5k | Code actions versus tool calls; sandbox boundary |
| [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | 20.4k | Configurable agent-computer interfaces; superseded for new work by mini-swe-agent |
| [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | 20.2k | Typed tools, output validation and durable-workflow integrations |
| [SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) | 8.0k | Minimal baseline, model/environment seam and budgets |
| [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench) | 5.9k | Reproducible patch evaluation and cache provenance |
| [anthropics/claude-agent-sdk-demos](https://github.com/anthropics/claude-agent-sdk-demos) | 2.8k | Worked hooks, delegation and session examples; local demos |
| [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk) | 1.2k | Execution implementation, isolated workspaces and remote server |

- Aider's README identifies repository mapping, automatic Git commits and lint/test feedback. These are useful worked examples for the existing discovery and verification notes. — [Aider](https://github.com/Aider-AI/aider)
- smolagents explicitly warns that its `LocalPythonExecutor` is not a security sandbox and supports both code-producing and conventional tool-calling agents. This distinction directly improves `Authority Policy` and tool-interface experiments. — [smolagents](https://github.com/huggingface/smolagents)
- PydanticAI's README demonstrates typed output models, argument validation before tool execution, dependency context and durable workflow integrations. Schema validity should be taught separately from factual correctness or authorization. — [PydanticAI](https://github.com/pydantic/pydantic-ai)
- AutoGen's README marks it maintenance mode and recommends Microsoft Agent Framework for new projects. Its Core, AgentChat and Extensions boundaries remain a useful architecture comparison. — [AutoGen](https://github.com/microsoft/autogen)

### Inferences
- **Opportunity 11: typed boundary tests.** Add `09 - Tools and Interfaces/Typed Outputs and Semantic Validation.md`, drawing on PydanticAI. Exercise an invalid schema, a valid schema with a false assertion, and a valid request lacking permission. Each needs a different failure response.
- **Opportunity 12: repository-map and edit-feedback lab.** Extend `Repository Discovery Funnel` using Aider's map as an alternative context-selection method. Measure whether selected files cover the dependency involved in a known bug; run lint/tests after edits and preserve their evidence. Compare with plain search rather than assuming maps always help.
- Fold smolagents into opportunity 2 as a third action representation and opportunity 4 as a concrete example of restrictions that are not a security boundary.
- Add an explicit `maintenance_status` source-card field: AutoGen and SWE-agent demonstrate why star counts alone should not choose a current implementation.

### Gaps
- Broader candidates can still exist above the threshold. The scan prioritized coding harnesses, orchestration, execution safety and evaluations; it did not enumerate every agent/RAG framework or awesome-list.
- The user's contextual repository `sakti1977/Harness-Engineering` could not be fetched through the web tool in this pass; no remote comparison is claimed. The local vault was used for gap analysis.
- The four additionally scanned projects (Aider, smolagents, AutoGen, PydanticAI) received README-level inspection, not deep module reviews. Do not present all 13 as equally audited.
