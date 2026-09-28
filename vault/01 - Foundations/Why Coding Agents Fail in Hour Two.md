---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - foundations
---

# Why Coding Agents Fail in Hour Two

## Problem

The first hour of an agent session usually goes well. The task is fresh, the context is small, and every change gets immediate feedback. Failures cluster later: the agent has read dozens of files, the conversation has been compacted or restarted, and the definition of done has quietly shifted from "the user's problem is gone" to "the tests I can see are green".

## Mechanism

Five things decay as a session gets longer, one per layer of the harness:

| What decays | Symptom | Layer |
| --- | --- | --- |
| The map of where behavior lives | The agent edits a plausible file instead of the one that owns the behavior | Reach |
| The boundary of the task | "While I'm here" edits to unrelated modules | Power and Scope |
| The environment | Checks run somewhere other than where the bug lives: one time zone, one database connection | Ground |
| The meaning of done | A response or helper test stands in for the outcome | Verdict |
| The memory of what was learned | A new session repeats a diagnosis, or trusts a stale summary | Carry |

None of these needs a worse model. They are properties of the environment around it, which is why the fix is a harness rather than a longer prompt.

## Worked example

In the repository's evaluation (`evals/jyotish`), agents received three user reports against a small astrology coaching app. Without a harness, both Claude Haiku 4.5 runs fixed the two visible bugs, missed a race between reading a chart and saving coaching, and still reported all three issues fixed. One run decided the race was a symptom of another bug; the other hid stale coaching from the read path while still storing it. With the harness (written claims, verification routes and gates), both runs fixed all three and reported accurately. Two runs per condition is a pilot, not a rate.

## Try it

Run `python3 -m examples.astro.demo`. Three checks that an agent would plausibly write stay green on the broken app; the checks at the right boundaries fail.

## Diagnose your own failure

When an agent's "done" turns out wrong, ask in order: could a fresh session find the owner of the behavior? Was the change bounded? Did the check run in the environment where the bug lives? Did the check observe the outcome or a proxy? Could the next session recover what was learned? Fix the first missing control you can demonstrate with a failing check, not all five at once.

## Limits

This is a diagnostic frame, not a measured law. The five-way split is this vault's organizing synthesis; see [[Source Coverage Index]].

## Connected concepts

- [[Five Layers of a Harness]]
- [[Claim-to-Proof Matrix]]
- [[Cold-Session Checkpoint]]
- [[Jyotish Coach Sync and Age Incidents]]
