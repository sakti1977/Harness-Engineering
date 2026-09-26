---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - reach
---

# Repository as Shared Context

## Core idea and problem
A file existing in a repository does not mean an agent can use it.

## How it works
Knowledge must be present, reachable, and authoritative. Failure modes: missing, unreachable, conflicting, inert. Give domain invariants and architecture a canonical home.

## Example / failure mode
Agent edits appointments route and misses existing availability module because ticket and repository vocabularies differ.

## Implementation and verification notes
Use root routes to docs/product.md, docs/architecture.md, docs/domain.md, docs/verify.md.

## Connected concepts
- [Recovery Audit](Recovery%20Audit.md)
- [AGENTS.md as a Map](AGENTS.md%20as%20a%20Map.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Make the authoritative source and its review trigger visible. See [Knowledge Base Maintenance](Knowledge%20Base%20Maintenance.md) for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [Source Coverage Index](../00%20-%20Start%20Here/Source%20Coverage%20Index.md).
