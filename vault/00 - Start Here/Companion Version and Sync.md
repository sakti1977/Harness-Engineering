---
type: maintenance
status: maintained
reviewed: 2026-10-14
---

# Companion Version and Sync

The public repository maintains canonical learning content in `vault/`. Its GitHub-friendly `docs/handbook/` is generated; never edit both copies independently. A separate Obsidian working copy can lag the public kit.

## Current boundaries

The September learning roadmap describes an earlier foundation. The public kit now includes adoption, transition and handoff mechanisms; its README links initial live-agent trials with their limits. Consult the executable docs and results at the revision you use before interpreting older pending items.

The minimal adoption walkthrough is a synthetic teaching exercise, not a production gate or a feature-ledger schema. Its measured verification is recorded in [[Vault Update Record]]. Unfamiliar-user completion time and transfer to real projects remain unmeasured.

## Synchronize a working copy

1. Record the public checkout revision with `git rev-parse HEAD`.
2. Compare edited Markdown with `vault/` and resolve newer changes before copying. Preserve unrelated edits.
3. Keep standalone lab copies identical under `examples/` and `vault/Labs/examples/`. Repo-only gate examples depend on `scripts/` and are excluded from mirroring.
4. Run modules from the checkout root, or from `Labs` in a standalone vault. Check both entry points when changing labs.
5. Run the contribution checks and `python3 scripts/export_handbook.py`, then `python3 scripts/check_docs.py`. Commit canonical and generated changes together.
6. Use a reviewed PR; an updated working vault is not a published release.
