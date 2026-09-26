---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Agent Harness and Evaluation Harness

## Problem

A successful conversation can still leave a broken application. Locate the failure before changing the prompt.

## Mechanism

The model proposes actions. The agent harness supplies context, tools, permissions, execution, budgets and state. The task environment contains the application being changed. An evaluation harness resets a task, runs an agent under a recorded configuration, captures its trace and grades the resulting state. A grader should not trust the agent’s completion message.

## Worked example

An agent says a booking conflict was fixed. Its helper returns 409, but two rows remain in the database. The response assertion passed; the final-state check did not. The task outcome is a failure even if every tool returned successfully.

## Try it and check the result

Use [First Executable Harness Lab](../11%20-%20Practical%20Implementations/First%20Executable%20Harness%20Lab.md). Identify the application, intentionally weak check, stronger outcome assertions and test runner. Write one claim each layer can establish. Finish when you can explain why the weak check passes the broken implementation.

## Tradeoffs and limits

Deterministic checks isolate a known mechanism. Live-agent trials evaluate the combined model and harness and can vary between attempts. Passing either kind does not imply the other kind passed.

## Sources and interpretation

[Anthropic: agent evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) supplies the agent/evaluation distinction and outcome-oriented grading.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Five Layers of a Harness](Five%20Layers%20of%20a%20Harness.md)
- [Harness-Control Tests](../10%20-%20Harness%20Testing/Harness-Control%20Tests.md)
- [Agent Evaluation Suite](../10%20-%20Harness%20Testing/Agent%20Evaluation%20Suite.md)
