---
type: index
status: maintained
reviewed: 2026-09-26
tags: [harness-engineering, repositories]
---

# Repository Pattern Atlas

Use repositories to study a mechanism and its limits. All 13 met the 1,000-star discovery threshold in the dated [research inventory](../research_notes/Harness%20knowledge%20base%20expansion/repositories.md). Counts and maintenance status are snapshots, not permanent recommendations. The practical question is what your project needs to verify.

## Execution and permissions

- [OpenAI Codex](https://github.com/openai/codex): inspect core policy and app-server contracts. Connect to [Sandbox Enforcement Matrix](../03%20-%20Power/Sandbox%20Enforcement%20Matrix.md) and [Budgets and Termination](../08%20-%20Agent%20Runtime/Budgets%20and%20Termination.md). Platform and version matter.
- [OpenHands](https://github.com/OpenHands/OpenHands): study the application and automation boundary. Its [Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) exposes execution/workspace concepts; treat these as two repositories with related responsibilities.
- [smolagents](https://github.com/huggingface/smolagents): compare code actions with tool calls. Its local executor is not a security sandbox; read [Typed Outputs and Semantic Validation](../09%20-%20Tools%20and%20Interfaces/Typed%20Outputs%20and%20Semantic%20Validation.md).

## Minimal agents and editing feedback

- [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent): inspect the agent/environment/model seam and budget loop. Use it as a baseline for [Harness Ablation Experiments](../10%20-%20Harness%20Testing/Harness%20Ablation%20Experiments.md).
- [SWE-agent](https://github.com/SWE-agent/SWE-agent): compare richer interfaces; its researched README directed new development toward mini-swe-agent. Recheck before adoption.
- [Aider](https://github.com/Aider-AI/aider): repository maps and lint/test feedback are comparison candidates for [Context Retrieval Experiments](../02%20-%20Reach/Context%20Retrieval%20Experiments.md).

## State, types and coordination

- [LangGraph](https://github.com/langchain-ai/langgraph): thread checkpoints versus shared stores; see [Memory Scope and Retention](../07%20-%20Carry/Memory%20Scope%20and%20Retention.md).
- [PydanticAI](https://github.com/pydantic/pydantic-ai): typed tool/output validation; see [Typed Outputs and Semantic Validation](../09%20-%20Tools%20and%20Interfaces/Typed%20Outputs%20and%20Semantic%20Validation.md).
- [AutoGen](https://github.com/microsoft/autogen): layered coordination as comparative material. The researched README marked maintenance mode; verify its successor guidance before starting new work.

## Product examples and evaluation

- [Claude Code](https://github.com/anthropics/claude-code): product-facing documentation and plugins; do not treat it as a complete runtime source release.
- [Claude Agent SDK demos](https://github.com/anthropics/claude-agent-sdk-demos): inspect hooks, research lineage and sessions. These are local demos with deployment limitations; see [Delegation and Shared State](../08%20-%20Agent%20Runtime/Delegation%20and%20Shared%20State.md).
- [SWE-bench](https://github.com/SWE-bench/SWE-bench): evaluation environment and cache provenance; see [Reproducible Evaluation Environment](../04%20-%20Ground/Reproducible%20Evaluation%20Environment.md).

## Adoption worksheet

For any candidate, record the exact release/commit, inspected files, maintenance status, license, required credentials, execution privileges and the fixture you will use to verify the relevant behavior. A README-level survey is not a code audit. Copy [Source Note Template](../Templates/Source%20Note%20Template.md) and link the resulting card from the concept it supports.
