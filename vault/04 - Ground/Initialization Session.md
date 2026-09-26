---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - ground
---

# Initialization Session

## Core idea and problem
A script printing READY can mask missing config, seed data, or unavailable service.

## How it works
Initialize in a distinct phase. Apply deterministic local repair; request missing access; stop destructive or ambiguous repair. Probe readiness rather than reporting activity.

## Example / failure mode
CLINIC_TIMEZONE missing, seed empty, health endpoint 503, yet init claims ready.

## Implementation and verification notes
Break one prerequisite, assert BLOCKED, repair, run twice for idempotence, then start a cold agent.

## Connected concepts
- [[Readiness Contract]]
- [[Verification Routes and Test Fidelity]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Anthropic’s long-running-agent account (S2) supplies external context for initializer and progress artifacts. See [[Source Register]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
