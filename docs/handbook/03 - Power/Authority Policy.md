---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - power
---

# Authority Policy

## Core idea and problem
Scope and sandbox alone cannot prevent destructive actions against intended systems.

## How it works
Deny by default. Specify read/write paths, executable+args, secrets, irreversible actions, approvals. Judge target resource and consequence, not scary command names. Emit typed refusal and safe escalation.

## Example / failure mode
db:reset points to a live clinic database; agent deletes bookings.

## Implementation and verification notes
Example refusal codes: SECRET_PATH_DENIED, PATH_OUTSIDE_SURFACE, COMMAND_NOT_ALLOWED, DESTRUCTIVE_ACTION_REQUIRES_APPROVAL. Agent cannot self-grant.

## Connected concepts
- [Secret Handling](Secret%20Handling.md)
- [Three Tools and One Permit](../09%20-%20Tools%20and%20Interfaces/Three%20Tools%20and%20One%20Permit.md)
- [Destructive Database Reset](../12%20-%20Case%20Studies/Destructive%20Database%20Reset.md)

## Reflection questions
- What specific failure would this concept prevent or reveal?
- Which artifact owns the rule, and how could we test that the rule works?
- What would a cold session need to recover this decision?

## Practical extension

Record which execution route actually enforces each policy; an instruction file alone cannot enforce it. See [Sandbox Enforcement Matrix](Sandbox%20Enforcement%20Matrix.md) for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [Source Coverage Index](../00%20-%20Start%20Here/Source%20Coverage%20Index.md).
