---
type: case-study
evidence_kind: instructional-scenario
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - case-studies
---

# Wrenfold Booking Failures

> **Evidence status:** an instructional scenario inherited from earlier shared material. No independently verified production incident is claimed.

## Core idea and problem
A clinic booking feature seems done but allows conflicts.

## How it works
Map wrong owner to Reach, broken seed to Ground, helper-only test to Verdict, lost diagnosis to Carry.

## Example / failure mode
Two concurrent bookings both return success and persist.

## Connected concepts
- [[Recovery Audit]]
- [[Verification Routes and Test Fidelity]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Reproduction route

Use [[Case Study Template]] to record evidence and uncertainty. The executable synthetic counterpart is [[First Executable Harness Lab]].
