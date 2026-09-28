# Authority Policy

Default: deny.

- Read: anything in this repository. Nothing outside it except the harness kit at `$HARNESS_KIT`.
- Write: `jyotish/app.py`, `tests/`, `docs/proof-matrix.md`, `docs/verify.md`, `.harness/checkpoint.md`.
- Never write: `.harness/feature.json`, `.harness/feature-log.jsonl` (change state only with the transition command), `.harness/evidence.json` (the verifier records evidence), this file, `AGENTS.md`, `CLAUDE.md`.
- Commands: `python3 -m unittest ...`, `git status`, `git diff`, and the harness commands. No installs, no network.
