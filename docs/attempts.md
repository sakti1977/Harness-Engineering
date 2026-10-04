# Attempts: run work once, stop when the outcome is unknown

An agent runs a task. The call times out. Two things could have happened: the work never ran, or it finished and only the response was lost. The agent cannot tell which, and it does not need to be confused to get this wrong. In the incident behind this control, the agent read every error correctly (a timeout, a locked record, a missing VPN) and still ran the task again, four times. The first run had already finished, and each repeat created more records behind a lock the first run had left.

Understanding a failure does not constrain what a model does next. So the constraint cannot live in the prompt. It lives in the executor: before anything with side effects starts, the intent is written to a ledger, and the same intent is refused until its outcome is known.

```sh
python3 -m examples.gate.timeout_demo    # a lost response, with and without the gate
```

```text
                              no gate     gate  gate, blind
suite executions                    4        1            1
records created                     4        1            1
failed attempts                     3        0            0
task confirmed finished            no      yes          yes
```

The demo is a simulation with a scripted agent. The counts are exact for it. They are not a measurement of a real agent, and they do not price the extra executions (wall-clock time, load on the environment, output a model has to read).

## The idea

A timeout is an observation, not an outcome. Every intent has a key built from what the work is (review, suite, environment, commit), never from when it ran. The ledger records the intent before the work starts and the outcome after. That gives an attempt one more state than success and failure:

| State | Meaning | May it start again? |
| --- | --- | --- |
| `submitting` | Intent written, no outcome yet: still running, or its caller died | No: reconcile first |
| `complete` | Finished | No: the recorded result is returned instead |
| `failed` | The work reported a definite failure | Yes, within a budget (default 3) |
| `unknown` | Timed out; it may have finished | No: reconcile first |
| `needs_inspection` | Reconciliation could not tell | No: a person decides |
| `released` | Reconciled or resolved as safe to run again | Yes |

Unknown has its own exits. There is no path from `unknown` straight back to running; it goes through a lookup by the original key, and through a person when the lookup cannot settle it.

## Use it

`scripts/harness_attempt.py run` wraps one command. Give it a key, who is running it and the command after `--`:

```sh
KEY=$(python3 scripts/harness_attempt.py key review-17 smoke staging "$(git rev-parse HEAD)")
python3 scripts/harness_attempt.py run --key "$KEY" --actor copilot-agent --timeout 600 \
    --precondition vpn="./scripts/check_vpn.sh" -- ./scripts/run_coverage_suite.sh
```

```text
OK key=3b8c... exit=0 seconds=212.4 lines=480 output=.harness/attempts/3b8c....out
<last 40 lines of output>
```

The full output is saved to the path shown, so an agent that needs more reads the file instead of running the suite again. Run the same key again and nothing executes:

```text
ALREADY DONE key=3b8c... completed at 2026-10-04T09:12:31Z; not run again. exit=0 seconds=212.4 lines=480 output=.harness/attempts/3b8c....out
```

If the timeout fires, or the wrapper is killed, the next call is refused with the next step:

```text
UNKNOWN key=3b8c...: no result after 600.0s. The work may have finished. Do NOT run it again.
REFUSED ATTEMPT_OUTCOME_UNKNOWN: the earlier attempt of 3b8c... timed out and may have finished (since 2026-10-04T09:12:31Z)
  next: Do not run it again. Find out what happened: python3 scripts/harness_attempt.py reconcile --key 3b8c... --actor NAME --probe "COMMAND" ...
```

| Exit | Meaning |
| --- | --- |
| 0 | Ran, or already done (nothing executed) |
| 1 | The command failed, or the gate refused |
| 2 | Usage error; nothing ran |
| 3 | Outcome unknown; do not run again |

| Command | Who | What it does |
| --- | --- | --- |
| `run` | agent | Runs one command at most once per key. The only command that executes your work |
| `status` | anyone | Every intent, the kill switch, and whether the ledger verifies |
| `reconcile --probe CMD` | agent | Runs your probe: exit 0 means the effect exists (complete), exit 1 means it does not (released), anything else means nobody can tell (`needs_inspection`) |
| `resolve --verdict complete\|rerun` | operator | Settles an uncertain attempt, or grants a fresh failure budget. The operator must not be the actor who started the attempt |
| `stop` / `go` | anyone / operator | The kill switch. `stop` refuses all new work; only an operator lifts it |
| `key PART...` | anyone | A stable key from the parts that identify the work |

**Write a probe that checks the effect, not the process.** A probe that says "I see nothing running" is not evidence that nothing ran. If the effect could be in flight, the probe should return "cannot tell" (any exit code other than 0 or 1), and a person decides.

From Python, `execute(root, key, payload, fn, actor=...)` does the same around a function: `fn` returns a result dict, raises `TimeoutError` when the outcome is unknown, and any other exception is a definite failure. `begin` and `record` split it for runners that start work now and report later.

## What the gate checks

| Code | Refused when | What the agent should do |
| --- | --- | --- |
| `ATTEMPT_OUTCOME_UNKNOWN` | The earlier attempt of this key has no recorded outcome | Reconcile; never run it again |
| `ATTEMPT_ALREADY_COMPLETE` | The key already completed. `run` returns the recorded result instead | Use the recorded result |
| `ATTEMPT_KILL_SWITCH` | An operator stopped execution. Finished work can still be replayed | Report and wait; never work around it |
| `ATTEMPT_PRECONDITION_FAILED` | A named prerequisite (VPN, an unresolved lock, environment state) is not met | Fix the prerequisite; repeating the work will not |
| `ATTEMPT_BUDGET_EXHAUSTED` | The key failed definitively too many times | Stop and report; an operator can grant a fresh budget |
| `ATTEMPT_KEY_PAYLOAD_MISMATCH` | The key was first used for different work | Derive a new key for new work |
| `ATTEMPT_LEDGER_INVALID` | The ledger's hash chain is broken or it is not valid | Execution stays blocked until an operator inspects it |
| `ATTEMPT_ROLE_DENIED` | A non-operator tried to resolve an attempt or lift the kill switch | Ask an operator |
| `ATTEMPT_RESOLVE_NOT_INDEPENDENT` | The operator started the attempt they are settling | A different operator settles it |
| `ATTEMPT_RESOLVE_NOT_PENDING` | There is nothing uncertain to reconcile or resolve | Nothing to do |

Prerequisites are only probed when the ledger does not already settle the question, so a finished key replays even if the VPN is down.

Each code has a defect fixture and the gate has clean fixtures in [harness tests](../harness-tests/README.md).

## Which actions belong behind it

Behind it are the actions whose repetition is not harmless. Reads are safe to repeat and do not need it.

| Action | Safe to repeat? | What makes it safe |
| --- | --- | --- |
| Read code, tests, designs, stories | Yes | Record which revisions were read, so a resumed review never mixes yesterday's run with today's source |
| Start a test run, a deploy, a migration, a ticket or a message | No | Run it through `run`, with a key from what it is |
| Poll status, fetch results | Yes | Keep these separate tools from the start tool. After a timeout while waiting, the next action is a status check |
| Test setup and cleanup that mutate state | Only with protection | Per-run fixtures, operations safe to repeat, or a verified reset; otherwise refuse another attempt until a person checks the environment |
| Save findings | Yes | Update by review ID, so saving twice does not produce two reports |

A finding that rests on a run whose outcome is unknown is `UNVERIFIED`, which is different from a confirmed gap. Do not report the first as the second.

## Protect it

The roles are labels. Nothing in this script stops an agent that can write the ledger from editing it. Enforcement comes from the [authority policy](authority.md) and the sandbox, so add the following to the project's policy:

- **Write denied:** `.harness/attempts.jsonl`, `.harness/attempts.lock`, `.harness/STOP`, `.harness/attempts/**` (only the commands above write them).
- **Commands allowed, as exact strings.** `run`, `reconcile --probe` and `--precondition` execute whatever command they are given, so allowing `python3 scripts/harness_attempt.py run *` would let the agent run any command through the wrapper: the same hole as `python3 *`. Put each fixed call in a small project script (for example `scripts/run_coverage_suite_once.sh`, which calls `run` with the key and the suite command) and allow that exact string. `status` and `stop` take no command and can be allowed as written. `resolve` and `go` are for the operator, not the agent.
- **Do not commit** the ledger, the stop file or the saved output. Add `.harness/attempts.jsonl`, `.harness/attempts.lock`, `.harness/attempts/` and `.harness/STOP` to `.gitignore` (this repository does).

## Limits

- The hash chain detects an edit to an earlier entry, a removed middle entry and a reordered one. It does not detect an edit to the last entry, truncation of the last entries, or a deleted ledger, which reads as empty. Protect the file; for stronger evidence, copy the ledger's last line hash somewhere the agent cannot write.
- It controls work that goes through it. A command run any other way is invisible to it.
- A timeout kills the command it started, but not necessarily the processes that command started. That is exactly why the outcome is recorded as unknown.
- Saved output is stored as the command printed it. It is not redacted, which is another reason to keep it out of version control and out of the agent's read permissions where it holds secrets.
- The ledger lock is a file created atomically. A lock left by a crashed holder is broken after 60 seconds. Two processes that both decide to break the same stale lock at the same instant could both proceed; that needs a crash and a collision.
- `released` by a probe is only as good as the probe.
- It does not replace idempotency at the receiver. If the service you call can deduplicate by key, pass the same key through, and the gate becomes the second line of defense.
- Early signal only: the demo simulates an agent. Run a real agent through it and measure.
