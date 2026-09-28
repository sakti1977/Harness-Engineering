---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - foundations
---

# Five Layers of a Harness

## Problem

Agent reliability problems are usually described as "the model got it wrong". That framing leads to longer prompts, which are the weakest control available: an instruction can be ignored, forgotten after compaction, or contradicted by the next instruction. A harness is the set of controls around the model that make the right outcome likely and the wrong outcome visible.

## The layers

| Layer | Question | Controls in this repository |
| --- | --- | --- |
| **Reach** | Can the agent find the right context and the owner of the behavior? | `AGENTS.md`, verification routes in `docs/verify.md` |
| **Power** | What may it read, write and run, and what stays off limits? | `docs/authority.md`, the scope contract, `harness_check.py --session` |
| **Ground** | Does the work run in an environment that is ready and faithful to production? | `docs/readiness.md`, fidelity checks in the routes |
| **Verdict** | What evidence proves each claim, beyond "tests pass"? | the proof matrix, the transition gate, evidence freshness |
| **Carry** | Can a fresh session pick up where the last one stopped? | the checkpoint, the handoff gate and the Resume Protocol |

The layers are a way to locate a failure, not a checklist to implement top to bottom. Most teams get the largest early gain from Verdict: writing down what "done" must prove.

## How to use them

1. Start from one failure you have actually seen.
2. Name the layer whose control would have caught it (see [Why Coding Agents Fail in Hour Two](Why%20Coding%20Agents%20Fail%20in%20Hour%20Two.md)).
3. Add the smallest control that makes that failure visible, and prove it fails on the defect and passes on the fix.
4. Keep controls with real consequences (a gate that refuses, a check that fails). Retest instruction-only controls when models change; some become unnecessary.

## Worked example

The Jyotish Coach lab has one defect per layer boundary: a "Synced" badge that only a persistence check exposes (Verdict), ages that only go wrong behind UTC (Ground), and a race that only shows up when a correction lands mid-generation (Ground and Verdict). The gate demo (`python3 -m examples.gate.demo`) shows Power and Verdict controls refusing an out-of-scope edit and a self-approval.

## Limits

Reach, Power, Ground, Verdict and Carry are this vault's organizing synthesis, not an external standard. The original source history is recorded in [Source Coverage Index](../00%20-%20Start%20Here/Source%20Coverage%20Index.md); externally attributed material is in [Source Register](../00%20-%20Start%20Here/Source%20Register.md). Compare the model with [Agent Harness and Evaluation Harness](Agent%20Harness%20and%20Evaluation%20Harness.md): the same vocabulary applies to the harness an agent works in and the harness that evaluates it.

## Connected concepts

- [Reach - MOC](../02%20-%20Reach/Reach%20-%20MOC.md)
- [Power - MOC](../03%20-%20Power/Power%20-%20MOC.md)
- [Ground - MOC](../04%20-%20Ground/Ground%20-%20MOC.md)
- [Verdict - MOC](../06%20-%20Verdict/Verdict%20-%20MOC.md)
- [Carry - MOC](../07%20-%20Carry/Carry%20-%20MOC.md)
