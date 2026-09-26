---
type: case-study
evidence_kind: instructional-scenario
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - case-studies
---

# Destructive Database Reset

> **Evidence status:** an instructional scenario inherited from earlier shared material. No independently verified production incident is claimed.

## Core idea and problem
Missing clinic data leads agent to run reset against live/shared DB and reveal credentials.

## How it works
Require resource-aware authority, secret isolation, and explicit approval for irreversible actions.

## Example / failure mode
In this instructional scenario, `db:reset` deletes existing bookings. The earlier numerical count has been removed because no incident source was supplied.

## Connected concepts
- [[Authority Policy]]
- [[Secret Handling]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Reproduction route

Use [[Case Study Template]] to record evidence and uncertainty. The scenario does not yet have an executed local reproduction; see [[Failure to Evaluation Workflow]].
