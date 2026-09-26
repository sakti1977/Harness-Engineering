---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - reach
---

# Repository Discovery Funnel

## Core idea and problem
Raw recursive listing is noisy; guessed paths create false confidence.

## How it works
List → fixed-text search → bounded read → follow authoritative references. Stable sort, ignore generated/dependency dirs, mark truncation, skip binary, include line refs; check lexical and resolved paths.

## Example / failure mode
Search for “appointment” finds route but not “availability”; follow domain vocabulary.

## Implementation and verification notes
Match limits cap context, not filesystem work; add file/time/cancel budgets.

## Connected concepts
- [[Repository as Shared Context]]
- [[Three Tools and One Permit]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Compare a repository map with plain search on tasks with known dependency paths. See [[Context Retrieval Experiments]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
