---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - practical-implementations
---

# Minimal Harness Adoption Path

## Problem

Teams that adopt a harness all at once build controls for failures they have never seen: ledgers, journals, compaction rules and sandboxes that cost maintenance and catch nothing. The result is ceremony, and the first time a control blocks real work it gets switched off.

## Mechanism

Grow the harness from observed failures, one control at a time:

1. **One failure.** Pick a failure your agent actually caused.
2. **One outcome and its claims.** Write the observable outcome and two to four claims, each with its required boundary.
3. **One real route.** A verification route that crosses those boundaries, and a seeded broken version it fails on.
4. **Scope and authority.** The files the change may touch, and what the agent may run.
5. **Then add, only when a failure asks for it:** the transition gate when more than one feature is in flight or "done" gets overclaimed; the handoff gate when sessions end mid-task; a journal for long unattended runs; a release gate for shipping.

After each addition, measure what it costs (tokens, time, friction) and retest it when models change. Some controls become unnecessary.

## Worked example

The Jyotish Coach lab shows the order in miniature. One real incident (a "Synced" badge over rejected writes) needs one claim with a `persistence` boundary and one route that reads the profile back. The age incident adds an `environment` boundary. The stale-coaching race adds a timing route and the sweep. The transition and handoff gates sit on top, and each has fixtures in `harness-tests/` proving it refuses the defect and passes clean work.

## Try it

```sh
python3 scripts/harness_adopt.py --root /path/to/project            # preview; writes nothing
python3 scripts/harness_adopt.py --root /path/to/project --apply    # create missing files; never overwrites
```

Adopt creates the first feature in state `planned` with TODOs, and prints the commit command for the files it created, so the first session check measures your work and not the setup. `docs/adoption.md` walks through describing one feature and working through the gates.

## Limits

Adopt sets up files; it does not know your domain, and every TODO needs a person. Instruction files are guidance: pair them with your agent tool's permission settings ([[Authority Policy]]). The evidence that this order helps is one author's projects and a small pilot, not a study.

## Connected concepts

- [[Five Layers of a Harness]]
- [[Harness-Control Tests]]
- [[Project Harness Assessment]]
- [[Scope Contract]]
