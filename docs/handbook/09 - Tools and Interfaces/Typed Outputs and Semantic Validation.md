---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Typed Outputs and Semantic Validation

## Problem

Valid JSON may contain false claims or describe an action the caller is not allowed to perform.

## Mechanism

Validate structure, meaning and authorization separately. Reject invalid field types before execution. Check domain invariants against current state. Evaluate authority at the resource boundary using authenticated context, not a role claimed inside model output.

## Worked example

A booking request has a correctly typed start and end, but end precedes start. Another is semantically valid but targets a forbidden tenant. These need different errors and neither should create a row.

## Try it and check the result

Write three fixtures: malformed structure, valid structure with an invalid interval, and a valid interval with denied authority. Assert distinct errors and unchanged persistent state. Add a permitted request to catch a validator that rejects everything.

## Tradeoffs and limits

A schema is not a security boundary or a truth checker. Coercion can hide errors; choose and document strictness. The booking lab exercises domain behavior, not tenant authentication.

## Sources and interpretation

[PydanticAI](https://github.com/pydantic/pydantic-ai) illustrates typed tools and validation. The three-stage separation is a local design recommendation.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [MCP Identity and Network Boundaries](../03%20-%20Power/MCP%20Identity%20and%20Network%20Boundaries.md)
- [Tool Usability Evaluations](Tool%20Usability%20Evaluations.md)
- [First Executable Harness Lab](../11%20-%20Practical%20Implementations/First%20Executable%20Harness%20Lab.md)
