---
type: concept
status: synthesized-from-shared-material
tags:
  - harness-engineering
  - verdict
---

# Feature Ledger as a Gate

## Core idea and problem
A feature list that agents can self-mark passing becomes a false memory for later sessions.

## How it works
Ledger fields id, behavior, state, depends_on, verification, evidence, blocked_on. Planner owns plan; worker requests; verifier owns verdict; invalidator revokes stale proof. Reject unauthorized transitions atomically.

## Example / failure mode
CLIN-511 marked passing although E2E failed; next session trusts it.

## Implementation and verification notes
Test no-evidence passing, duplicate IDs, missing dependencies, unauthorized planner edits, stale revision; rejected ledger remains byte-identical.

## Connected concepts
- [[Claim-to-Proof Matrix]]
- [[Scope Contract]]
- [[Harness-Control Tests]]

## Practical extension

The starter now implements this gate. `scripts/harness_transition.py` applies the transition policy (planner, worker and verifier roles; a verifier independent of the requester for `passing`; scope and evidence gates) and appends to a hash-chained audit log. `scripts/harness_check.py` replays that log on every run and flags edited history, direct state edits and stale proof. Run `python3 -m examples.gate.demo` to see each shortcut refused. Roles are declared rather than authenticated, so protect the log with repository review rules. See [[Project Harness Assessment]] for the worked exercise and primary-source context. This addition does not change the legacy provenance recorded in [[Source Coverage Index]].
