---
type: glossary
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - start-here
---

# Glossary

## Core idea and problem
Shared terminology prevents confusing ability, authorization, readiness, and proof.

## How it works
- **Reach:** discoverable authoritative knowledge.
- **Power:** capability plus permission.
- **Ground:** meaningful runtime and data.
- **Verdict:** independent claim-level evidence.
- **Carry:** durable continuity.

- **Proof gap:** difference between claim and observed test surface.
- **First divergence:** earliest event where actual differs from expected.
- **Replay:** read-only history inspection.
- **Resume:** new work after safe history.
- **Fork:** independent child from safe history.

## Example / failure mode
A test runner is Power; its assertion is Verdict. A startup command is Power; a successful readiness probe is Ground.

## Implementation and verification notes
See individual notes for contracts and failure cases.

## Connected concepts
- [[Five Layers of a Harness]]
- [[Claim-to-Proof Matrix]]
- [[Resume Replay and Fork]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Evaluation and operation terms

- **Agent harness:** the runtime around the model: context, actions, policy, state and budgets.
- **Evaluation harness:** the system that initializes tasks, executes trials and grades outcomes.
- **Trial:** one attempt under a recorded configuration.
- **Grader:** a mechanism judging an outcome or required constraint.
- **Capability suite:** tasks probing what the system can accomplish.
- **Regression suite:** cases protecting behavior already achieved.
- **Ablation:** remove or alter a mechanism and compare under controlled conditions.
- **Holdout:** tasks reserved from iterative optimization; exposure reduces independence.
- **Idempotency:** repeated requests with the same logical identity have the intended single effect under the receiver’s contract.
- **Outcome unknown:** a request’s effect may have occurred although no reliable receipt arrived.
- **Documented / configured / exercised / enforced:** increasingly specific descriptions that require evidence; file presence alone cannot establish enforcement.

See [[Agent Evaluation Suite]], [[Retry and Idempotency Contract]] and [[Project Harness Assessment]].
