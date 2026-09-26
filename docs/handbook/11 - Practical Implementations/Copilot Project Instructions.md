---
type: concept
status: maintained
reviewed: 2026-09-26
evidence_kind: implementation-and-local-guidance
---

# Copilot Project Instructions

## Role

An instruction file supplies navigation and behavior guidance. It does not implement a sandbox or independently verify completion.

## This repository’s actual starting point

[The original instructions](https://github.com/sakti1977/Harness-Engineering/blob/a800a594297451eab10e6ff0c9cde94a3e31aca0/.github/copilot-instructions.md) describe Reach, Scope, Power, editing, Ground, Verdict and Carry. They do not contain a full set of product or architecture documents. Earlier wording suggesting all such routes already existed has been corrected.

In the updated starter, core artifact checks are tool-neutral. Selecting `--adapter copilot` additionally checks that `.github/copilot-instructions.md` exists and is readable; this does not verify Copilot loaded or followed it.

## Adaptation exercise

Read your project’s existing instructions before editing. Add links to authoritative scope, authority, readiness and verification material. Keep commands exact and reviewable. Add a deliberately broken application fixture so compliance claims can be tested outside the conversation.

## Sources and limits

The repository file is implementation evidence for this project only. Agent-specific instruction loading can change; verify the current product contract before building an adapter. See [Repository Pattern Atlas](../13%20-%20Research/Repository%20Pattern%20Atlas.md), [AGENTS.md as a Map](../02%20-%20Reach/AGENTS.md%20as%20a%20Map.md), [Authority Policy](../03%20-%20Power/Authority%20Policy.md) and [Project Harness Assessment](Project%20Harness%20Assessment.md).
