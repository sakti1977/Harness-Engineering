# Session handoff: checkpoint, handoff gate and Resume Protocol

Sessions end with work in progress. The failure is not the unfinished work; it is a handoff that hides it. A checkpoint records the repository as it is, keeps verified facts apart from suspicions, and gives the next session a way to prove the direction is still valid. A stale handoff is treated as a failed check, not as guidance.

Anthropic's [long-running agent harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) used a progress file, a feature list and git history so each fresh session could recover what had been done and what to do next. Their initializer wrote `claude-progress.txt`; the name is incidental. Here the checkpoint is `.harness/checkpoint.md`, the feature list is the gated ledger, and the handoff is executable.

## Ending a session: the handoff gate

| Step | How |
| --- | --- |
| Refresh the diff and remove accidental edits | `git status`, `git diff`; `--check` flags uncommitted files outside the feature's scope |
| Run the strongest affordable check | The feature's verification command or a route in [verify.md](verify.md); if the environment blocks it, record the blocker and the exact command still to run |
| Update the ledger only with evidence that exists | `scripts/harness_transition.py`; its gates refuse states the evidence does not support |
| Rewrite the checkpoint from the observed repository | `python3 scripts/harness_handoff.py --write`, then fill the hand-written sections |
| Read it once as if the conversation had disappeared | `python3 scripts/harness_handoff.py --check`, then `--resume` |

`--write` records uncommitted files as they are, without a ceremonial commit. It lists each claim under **Verified at this state** only when `.harness/evidence.json` has a passing entry and no project file has changed since. Every other claim goes under **Not verified since the last edit**, with the command that would verify it. Suspected causes, blockers, decisions, the first command, the next bounded edit and grants are hand-written, and survive rewrites.

`--check` fails with:

| Code | Meaning |
| --- | --- |
| `SCOPE_OUTSIDE_SURFACE`, `SCOPE_EXCLUDED` | An uncommitted file is outside the feature's scope: an accidental edit, or a scope change to record |
| `CHECKPOINT_MISSING_FIELD` | A header line or section is missing, or the next edit or first command is not specific |
| `CHECKPOINT_STALE` | The checkpoint's revision, uncommitted files or feature state do not match the repository |
| `CHECKPOINT_OVERCLAIM` | A claim is presented as verified without current evidence |
| `CHECKPOINT_UNDECLARED_UNVERIFIED` | A claim without current evidence is not declared as unverified |
| `HANDOFF_UNREADABLE` | The repository or checkpoint cannot be read |

## Starting a session: the Resume Protocol

`python3 scripts/harness_handoff.py --resume` answers eight questions, each with its evidence source:

1. What outcome is active, and in what state?
2. Which revision and uncommitted files does the handoff describe, and do they still match?
3. Which claims are verified, by which command, at which revision?
4. Which claims are not verified since the last edit?
5. What is suspected but not verified?
6. What is blocked, and which command still needs to run?
7. Which decisions and constraints must be preserved?
8. What is the first command, and the next bounded edit?

A checkpoint that has never been written (the template a new project starts with) means there is no handoff yet: `--resume` passes and says to start from the ledger and routes. The handoff gate still refuses the template, so every session must write one before it ends.

If a written checkpoint is stale or incomplete, it fails and says so: re-derive the state from the repository before acting, then rewrite the checkpoint. The protocol lives in [AGENTS.md](../AGENTS.md), which `CLAUDE.md` and the Copilot instructions point to.

## Testing the handoff

- **Recovery audit.** Open a session with no conversation history and require it to answer the eight questions with a file or command as evidence before it changes code. Any guess exposes a missing field or an unclear instruction: repair, restart, repeat.
- **Stale detection.** Change the repository after writing the checkpoint and confirm `--resume` reports `CHECKPOINT_STALE` instead of following stale guidance. The harness tests do this automatically for a later commit, a later edit, a later state change and evidence that went out of date after the handoff.

## Limits

- The checkpoint's hand-written sections are only as honest as their author; the gate checks their presence and specificity, not their truth.
- Staleness is judged on revision, uncommitted files and feature state. A change outside git (a database, a remote service) is invisible to it; record it under blockers or decisions.
