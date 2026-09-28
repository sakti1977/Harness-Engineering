---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - scope
---

# Scope Contract

## Problem

Agents drift. An atomic fix grows into renames, reformatting and a refactor; eleven files change while the reported behavior is still broken. The diff looks productive, review gets harder, and the scope of what has to be verified quietly expands.

## Mechanism

Every non-trivial task states five things before work starts:

1. **Outcome:** one externally observable behavior.
2. **Expected surface:** the files likely to change.
3. **Exclusions:** related work this task does not fund.
4. **Evidence:** the commands and assertions that prove completion.
5. **Discovery rule:** what to do with work found outside scope.

During the task, a necessary dependency outside the surface is an **amendment** (recorded with a reason); useful but unneeded work is **queued**; the task is **blocked** only for an external permission, decision or dependency. Completion is a verified outcome plus a final diff that reconciles with the scope. File count is not a quality measure.

## Worked example

In this repository the contract lives in `.harness/feature.json`: the outcome for the Jyotish lab, an `expected_surface` of `examples/astro/astro.py` and its test, and exclusions such as ephemeris accuracy and the voluntary contribution (UPI) flow. In the gate demo, an agent also edits `app/support/upi.py` and asks for verification: `SCOPE_OUTSIDE_SURFACE app/support/upi.py: Not in expected_surface: amend the scope with a reason, or revert.`

## Try it

```sh
echo "# drift" >> README.md
python3 scripts/harness_check.py --session     # SCOPE_OUTSIDE_SURFACE README.md
git checkout -- README.md
```

## Limits

The session check compares paths, not intent: a one-line fix and a rewrite of the same file look the same. Maintenance work on the harness itself shows up as out of scope when the ledger describes a teaching feature; that is the check doing its job, and the answer is a ledger for the maintenance task, not a wider surface. Authority over *how* files change is in [[Authority Policy]].

## Connected concepts

- [[Feature Ledger as a Gate]]
- [[Claim-to-Proof Matrix]]
- [[Authority Policy]]
- [[Task Contract Template]]
