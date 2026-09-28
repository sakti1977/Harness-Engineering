---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - reach
---

# Recovery Audit

## Problem

A fresh session has only the repository. If the route to the owner of a behavior, the setup command or the verification is not findable, the agent guesses: it patches the first plausible file, invents an endpoint, or reruns a check that cannot judge the claim.

## Mechanism

Audit navigation with a cold agent and four moves:

| Move | Question |
| --- | --- |
| **Root** | Does the entry file say where to start? |
| **Route** | Can the agent find the owner of the behavior from there? |
| **Check** | Can it find and run the verification for the claim? |
| **Remove** | Is there stale guidance that sends it the wrong way? |

Give a session with no history one task: find the owner, run setup, locate the invariant, reproduce the failing test. Observe what it reads *before* editing. Repair navigation (a route in `AGENTS.md`, a verification route in `docs/verify.md`) rather than adding prompt length.

## Worked example

Asked to fix "my age is a day early", a cold agent in the Jyotish lab should reach `age_on()` in `examples/astro/astro.py` through `AGENTS.md` and the `age-by-timezone` route, and reproduce the failure at UTC-5. If it instead edits the display layer, or tests only at UTC+5:30, the route is missing or buried, not the model's diligence.

## Try it

Run the audit against the handoff:

```sh
python3 scripts/harness_handoff.py --resume
```

It must answer all eight recovery questions with a file or command before any edit. Then change the repository after writing a checkpoint and confirm `--resume` reports `CHECKPOINT_STALE` instead of guidance.

## Limits

The audit measures one agent on one day. Repeat it when models change: some routes become unnecessary, and new failure patterns appear. It checks findability, not correctness of what is found.

## Connected concepts

- [[Repository as Shared Context]]
- [[Cold-Session Checkpoint]]
- [[AGENTS.md as a Map]]
