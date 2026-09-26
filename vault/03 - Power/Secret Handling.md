---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - power
---

# Secret Handling

## Core idea and problem
Credentials can leak through reads, env dumps, shell expansion, traces, and checkpoint text.

## How it works
Deny secret-bearing reads; inject needed credentials into runner without exposing values; redact events/reports; forbid indirect dumps.

## Example / failure mode
Agent prints a database URL while debugging missing seed data.

## Implementation and verification notes
Test direct .env read, printenv, shell expansion, and journal redaction.

## Connected concepts
- [[Authority Policy]]
- [[Append-Only Journal]]

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Minimize available credentials and trace content before relying on redaction. See [[Untrusted Content and Prompt Injection]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
