---
type: index
status: maintained
reviewed: 2026-09-26
tags: [harness-engineering, sources]
---

# Source Register

The original notes came from earlier shared material whose authorship and publication cannot be recovered here. [[Source Coverage Index]] preserves that thematic mapping. Sources below support the new explanations; they do not retroactively establish the origin of the five-layer vocabulary or clinic stories.

## How to use evidence

- **Primary engineering report:** direct account from its authors; findings may be workload-specific and unreplicated.
- **Implementation documentation:** supports behavior for the inspected version, not every configuration.
- **Local synthesis:** our teaching design or recommendation, explicitly identified as such.
- **Executed local result:** a command and observed output recorded in [[Vault Update Record]].

All sources were accessed during this task on 2026-09-26. Repository main links are moving references unless pinned. Publication dates are recorded only where verified. Star counts live in the dated research inventory and are not quality scores. Use [[Source Note Template]] for deeper source cards.

## Engineering articles

- **S1:** [OpenAI: harness engineering](https://openai.com/index/harness-engineering/). Published: 2026-02-11. Scope: Repository knowledge, mechanical checks, observability; one organization’s invested-in environment.
- **S2:** [Anthropic: long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). Published: 2025-11-26. Scope: Initializer and progress artifacts for long-running application work.
- **S3:** [Anthropic: context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). Published: 2025-09-29. Scope: Context selection, retrieval and durable notes.
- **S4:** [Anthropic: writing effective tools](https://www.anthropic.com/engineering/writing-tools-for-agents). Published: 2025-09-11. Scope: Tool interface quality and realistic evaluations.
- **S5:** [Anthropic: agent evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Published: 2026-01-09. Scope: Tasks, trials, outcomes and grader calibration.
- **S6:** [Anthropic: harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps). Published: 2026-03-24. Scope: Model-dependent scaffolding and evaluator experiments.
- **S8:** [LangChain: Better Harness](https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals). Published: 2026-04-08. Scope: Baseline, failure analysis, optimization and held-out cases.
- **S9:** [Anthropic: infrastructure noise](https://www.anthropic.com/engineering/infrastructure-noise). Published: 2026-02-05. Scope: Resource configuration as an evaluation variable.
- **S10:** [Anthropic: multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system). Published: 2025-06-13. Scope: Research-task delegation and overhead; not a universal coding result.
- **S11:** [Anthropic: containment](https://www.anthropic.com/engineering/how-we-contain-claude). Published: 2026-05-25. Scope: Environmental containment and content trust; defenses have limits.
- **S12:** [Anthropic: prompt injection defenses](https://www.anthropic.com/news/prompt-injection-defenses). Published: not recorded. Scope: Prompt injection in browser use and layered defenses.

S7 (LangChain’s Deep Agents benchmark account) remains in [[engineering_sources]]; this expansion does not reuse its numerical uplift as a local claim.

## Specifications and implementation references

- [MCP: security best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices). See the linked concept note for the claim used; pin a version before adopting executable integrations.
- [OpenTelemetry: agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md). See the linked concept note for the claim used; pin a version before adopting executable integrations.
- [AWS: making retries safe](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/). See the linked concept note for the claim used; pin a version before adopting executable integrations.
- [AWS: backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/). See the linked concept note for the claim used; pin a version before adopting executable integrations.
- [LangGraph: persistence](https://docs.langchain.com/oss/python/langgraph/persistence). See the linked concept note for the claim used; pin a version before adopting executable integrations.
- [Codex: core implementation notes](https://github.com/openai/codex/blob/main/codex-rs/core/README.md). See the linked concept note for the claim used; pin a version before adopting executable integrations.
- [Codex: app-server protocol](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md). See the linked concept note for the claim used; pin a version before adopting executable integrations.
- [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent). See the linked concept note for the claim used; pin a version before adopting executable integrations.
- [PydanticAI](https://github.com/pydantic/pydantic-ai). See the linked concept note for the claim used; pin a version before adopting executable integrations.

## Repository discovery

[[Repository Pattern Atlas]] maps the 13 repositories selected in [[repositories]] to learning questions and local notes. Review depth varies. No upstream benchmark or deployment was reproduced during the source survey.

## Review triggers

Revisit claims when a cited page changes, a model/runtime is upgraded, an adapter fails, a specification changes or a reader supplies conflicting evidence. Mechanical link validation and semantic source review are separate activities. See [[Knowledge Base Maintenance]].
