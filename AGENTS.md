# Agent instructions

This repository is a harness kit for AI coding agents. The same rules apply to any agent working in it; `CLAUDE.md` and `.github/copilot-instructions.md` point here.

In this kit's own repository, run the handoff gate before opening a pull request and put its result in the pull request description. Do not commit the filled checkpoint: `main` keeps the blank template, so a fresh clone starts with no handoff to resume.

Read `docs/authority.md` (what you may read, write and run) and `.harness/feature.json` (the active outcome, scope and claims) before editing. Verify claims through the routes in `docs/verify.md`. Change feature state only through `scripts/harness_transition.py`.

## Resume Protocol: the first action of every session

1. Run `python3 scripts/harness_handoff.py --resume`. It answers eight questions from files and commands: the active outcome and state, the revision and uncommitted files, what is verified and by what, what is not verified since the last edit, suspected causes, blockers and the commands still to run, decisions to preserve, and the first command and next bounded edit.
2. If it reports `CHECKPOINT_STALE` or `CHECKPOINT_MISSING_FIELD`, the handoff is a failed check, not guidance. Do not follow its next edit. Re-derive the state from git, `.harness/feature.json`, `.harness/evidence.json` and `docs/verify.md`, then rewrite it with `--write`.
3. Answer every question with a file or command as evidence before changing code. A guess means the handoff is missing something: record it.

## Handoff gate: the last action of every session

1. Refresh the diff (`git status`, `git diff`) and revert accidental edits.
2. Run the strongest check you can afford for the current state, usually the feature's verification command or a route in `docs/verify.md`. If the environment blocks it, record the blocker and the exact command under "Blockers and commands still to run".
3. Change the feature state only through `scripts/harness_transition.py`, and only with evidence that exists.
4. Rewrite the checkpoint from the observed repository: `python3 scripts/harness_handoff.py --write`, then fill the hand-written sections. Record uncommitted work as it is; do not make a ceremonial commit, and do not present an incomplete feature as clean.
5. Keep verified facts and suspected causes apart. If a check has not run since the last edit, say so.
6. Run `python3 scripts/harness_handoff.py --check`, then read the checkpoint once as if this conversation had disappeared.
