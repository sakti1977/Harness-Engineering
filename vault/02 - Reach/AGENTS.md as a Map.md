---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - reach
---

# AGENTS.md as a Map

## Problem

Root instruction files grow into encyclopedias. Every incident adds a paragraph; nothing is removed. Old advice (convert times to UTC here) contradicts new code (times are already UTC) and causes the bug it was written to prevent, while the constraints that matter now are buried.

## Mechanism

Place each piece of guidance with a four-way test:

| Placement | When |
| --- | --- |
| **Root** | It applies to every task in the repository |
| **Route** | It applies to some tasks: link to the file that owns it |
| **Check** | It can be asserted by a command: write the check instead of the sentence |
| **Remove** | It is expired, duplicated or contradicted by code |

"Critical" does not mean "global". Keep the root short: the system boundary, essential commands, global constraints, routes, and the completion command.

## Worked example

This repository's `AGENTS.md` is about twenty lines. It names the files to read before editing (`docs/authority.md`, `.harness/feature.json`), the route to verification (`docs/verify.md`), the one way to change feature state (`scripts/harness_transition.py`), and two protocols: the Resume Protocol at the start of a session and the handoff gate at the end. `CLAUDE.md` is one include (`@AGENTS.md`) and `.github/copilot-instructions.md` points to it, so three agents read one map. Everything else is a route or a check.

## Try it

`python3 scripts/harness_adopt.py --root /path/to/project` previews the same structure for another project, with `--agents` choosing which instruction files point at `AGENTS.md`. Then take your current root instructions and label every paragraph Root, Route, Check or Remove.

## Limits

The illustration of stale time zone advice is an instructional scenario, not a sourced incident. A short map depends on the routes it links to being current; a [[Recovery Audit]] is how you find out.

## Connected concepts

- [[Recovery Audit]]
- [[Claim-to-Proof Matrix]]
- [[Copilot Project Instructions]]
- [[Architecture Rules as Executable Checks]]
