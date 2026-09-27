# Checkpoint

Write this from the observed repository as the last action of every session: `python3 scripts/harness_handoff.py --write`, fill the hand-written sections, then `python3 scripts/harness_handoff.py --check`. The next session starts with `python3 scripts/harness_handoff.py --resume`. Facts are observed; anything under Suspected causes is not. Uncommitted work is recorded as it is: a checkpoint does not need a ceremonial commit.

- Written: <UTC time>
- Feature: <feature id> (state: <state from .harness/feature.json>)
- Revision: <git rev-parse HEAD>
- Uncommitted files: <paths from git status, or none>

## Verified at this state

<claim>: `<command>` passed at <revision>. Only claims with current evidence in .harness/evidence.json.

## Not verified since the last edit

<claim>, plus the command that would verify it. Every claim without current evidence belongs here.

## Suspected causes (not verified)

<hypothesis and what would confirm or refute it>

## Blockers and commands still to run

<what blocked verification, and the exact command that still needs to run>

## Decisions to preserve

<decision and why; constraints the next session must not undo>

## First command for the next session

`python3 scripts/harness_handoff.py --resume`

## Next bounded edit

<one edit, the file it touches, and the check that shows it worked>

## Grants used this session

<id, action, resource, approver, reason; grants expire with the session>
