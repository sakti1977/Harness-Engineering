# Feature transitions: the ledger as a gate

A feature list that an agent can edit freely is a memo: the next session trusts whatever the last one wrote. This kit turns `.harness/feature.json` into a gate. State changes go through one command, each change must satisfy a policy, and every accepted change is written to an append-only audit log that the checker replays.

```sh
python3 -m examples.gate.demo      # watch an agent's shortcuts get refused
```

## Transition policy

| From | To | Who may do it | Gate |
| --- | --- | --- | --- |
| (none) | `planned` or `active` | planner | Adopts the ledger; the first log entry |
| `planned` | `active` | planner, worker | Records the revision where work starts |
| `active` | `blocked` | planner, worker | Reason names the blocker |
| `blocked` | `active` | planner, worker | Reason names what unblocked it |
| `active` | `ready_for_verification` | worker | **Scope:** no file changed since work started is outside `expected_surface` or inside `excluded_paths`. **Proof plan:** every claim has a [proof-matrix](proof-matrix.md) row with a producer and no boundary gap |
| `ready_for_verification` | `active` | worker, verifier | Reason, e.g. the check that failed |
| `ready_for_verification` | `passing` | verifier | **Independence:** not the actor who requested verification. **Evidence:** every claim has passing evidence, no project file changed since it was recorded, clean working tree |
| `passing` | `active` | planner, verifier | Reopens stale or regressed work |

Anything else is refused, including `active -> passing`. A refused transition changes no file.

## Commands

```sh
# Adopt the ledger (planner), then work (worker)
python3 scripts/harness_transition.py --to planned --actor sakti --role planner --reason "BOOK-1 scoped"
python3 scripts/harness_transition.py --to active --actor copilot-agent --role worker --reason "start BOOK-1"

# Agent finishes: the scope gate runs
python3 scripts/harness_transition.py --to ready_for_verification --actor copilot-agent --role worker --reason "claims covered"

# A different person or CI job verifies: the evidence and independence gates run
python3 scripts/harness_transition.py --to passing --actor sakti --role verifier --reason "reviewed evidence"

# Any time: replay the log and check the current session
python3 scripts/harness_check.py --session
```

Record evidence in `.harness/evidence.json` (see [the schema](../schemas/evidence.schema.json)). Append one entry per verification run; the latest entry for each claim counts, and the claim text must match `feature.json` exactly.

```json
[
  {"claim": "conflicting booking creates no persistent row",
   "command": "python3 -m unittest examples.booking.test_booking -v",
   "result": "pass", "revision": "4a0a9d2", "observed": "row count stayed 1"}
]
```

## Audit log

`.harness/feature-log.jsonl` holds one JSON object per line: sequence number, UTC time, feature id, from, to, actor, role, git revision, reason, and the SHA-256 of the previous line. A `passing` entry also snapshots the claims it verified. Commit the log with your work.

On every run, `harness_check.py` replays the log and fails on:

| Code | Meaning |
| --- | --- |
| `LOG_CHAIN_BROKEN` | An entry was edited, removed or reordered |
| `LOG_REWRITTEN` | The committed log (or the `--base` revision's log) is not a prefix of the current one |
| `TRANSITION_NOT_ALLOWED`, `TRANSITION_ROLE_DENIED`, `TRANSITION_NOT_INDEPENDENT` | A hand-written entry breaks the policy, even with a valid hash |
| `STATE_MISMATCH` | `feature.json` was edited directly instead of through a transition |
| `PASSING_WITHOUT_LOG` | `passing` claimed with no log behind it |
| `PASSING_STALE` | Project files or claims changed after verification; reopen and verify again |

## Why this holds across sessions

A new session does not need the old conversation. The log says what state the feature is in, who moved it there, from which revision, and why. The start revision of the active entry is the scope baseline, so the scope gate works even after a context reset. `PASSING_STALE` is the invalidator: proof expires when the code it proved changes.

## Limits

- **Roles are declared, not authenticated.** An agent can pass `--role verifier --actor someone-else`. Real enforcement comes from where the log is written: protect `.harness/feature-log.jsonl` with CODEOWNERS and branch protection, and let `passing` be recorded only by a human reviewer or a CI job. The checker then catches any entry that breaks the policy.
- **Evidence is recorded, not re-run.** The gate checks that evidence exists, passed, and is newer than the code. It does not execute your verification command. Run trusted commands in CI and have CI write the evidence.
- **The hash chain detects edits; it does not prevent them.** Anyone with write access can rebuild a consistent chain. `LOG_REWRITTEN` catches that against committed history, which is why the log belongs in git.
- One feature per ledger in this release. Multi-feature ledgers and dependencies are future work.
