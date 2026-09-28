# Agent instructions

The harness kit is at `$HARNESS_KIT` (the path you were given with this task). Run its commands from this repository with `--root .`.

Before editing, read `docs/authority.md`, `.harness/feature.json` (the outcome, scope and claims) and `docs/verify.md` (how each claim must be proven).

Working rules:
1. Start work with `python3 $HARNESS_KIT/scripts/harness_transition.py --root . --to active --actor <your model name> --role worker --reason "start"`.
2. For each claim, write a test that follows its route in `docs/verify.md`, and see it fail on the current code before fixing the code.
3. Fill each claim's row in `docs/proof-matrix.md` (evidence producer, tested boundary, gap) and the route's command.
4. When every claim's test passes, request verification: `python3 $HARNESS_KIT/scripts/harness_transition.py --root . --to ready_for_verification --actor <your model name> --role worker --reason "..."`. You cannot mark the feature passing; a separate verifier does that.
5. Check the session any time with `python3 $HARNESS_KIT/scripts/harness_check.py --root . --session`.

## Resume Protocol: the first action of every session

1. Run `python3 $HARNESS_KIT/scripts/harness_handoff.py --root . --resume`. It answers eight questions from files and commands: the active outcome and state, the revision and uncommitted files, what is verified and by what, what is not verified since the last edit, suspected causes, blockers and the commands still to run, decisions to preserve, and the first command and next bounded edit.
2. If it reports `CHECKPOINT_STALE` or `CHECKPOINT_MISSING_FIELD`, the handoff is a failed check, not guidance. Do not follow its next edit. Re-derive the state from git, `.harness/feature.json`, `.harness/evidence.json` and `docs/verify.md`, then rewrite it with `--write`.
3. Answer every question with a file or command as evidence before changing code. A guess means the handoff is missing something: record it.

## Handoff gate: the last action of every session

1. Refresh the diff (`git status`, `git diff`) and revert accidental edits.
2. Run the strongest check you can afford for the current state, usually the feature's verification command or a route in `docs/verify.md`. If the environment blocks it, record the blocker and the exact command under "Blockers and commands still to run".
3. Change the feature state only through `$HARNESS_KIT/scripts/harness_transition.py`, and only with evidence that exists.
4. Rewrite the checkpoint from the observed repository: `python3 $HARNESS_KIT/scripts/harness_handoff.py --root . --write`, then fill the hand-written sections. Record uncommitted work as it is; do not make a ceremonial commit, and do not present an incomplete feature as clean.
5. Keep verified facts and suspected causes apart. If a check has not run since the last edit, say so.
6. Run `python3 $HARNESS_KIT/scripts/harness_handoff.py --root . --check`, then read the checkpoint once as if this conversation had disappeared.
