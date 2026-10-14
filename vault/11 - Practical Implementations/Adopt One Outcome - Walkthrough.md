---
type: walkthrough
status: maintained
evidence_kind: executed-synthetic-fixture
reviewed: 2026-10-14
---

# Adopt One Outcome - Walkthrough

A minimal harness starts with an observable outcome, a change boundary and a check that catches a known defect. This exercise gives you a complete disposable project with all three filled in. Allow about 20–30 minutes as a planning estimate; independent completion time has not been measured.

## What you will produce

A reviewed fix that rejects duplicate bookings, a regression that detects the defect, and a checkpoint another developer can use. You need Python 3.10+, a terminal and this vault. No model, credentials, packages or network are needed. You should be comfortable running Python commands; no harness framework knowledge is assumed.

## 1. Create the sample project

From an Obsidian vault copy, enter `Labs`. From a GitHub checkout, stay at the repository root and omit `cd Labs`:

```sh
cd Labs
python3 -m examples.adoption.project create /tmp/booking-starter
```

Use a different unused path if that directory exists. The command refuses to reuse existing directories. On Windows, substitute a writable unused directory for `/tmp/booking-starter`.

The generated project contains these complete artifacts:

- `booking.py`: the intentionally defective application.
- `test_booking.py`: three outcome assertions, including concurrent requests.
- `task.md`: outcome, allowed edits, exclusions, acceptance and authority.
- `proof.md`: each claim, its test and the boundary it proves.
- `checkpoint.md`: the observed initial state and next command; no passing claim.

Read `task.md` and `proof.md` before editing. The generator's [source](../Labs/examples/adoption/project.py) contains every filled artifact.

## 2. Observe the defect

In a second terminal, enter the generated project:

```sh
cd /tmp/booking-starter
python3 -m unittest test_booking -v
```

Expected: three tests run, with exactly two assertion failures. A valid booking passes. Duplicate and simultaneous requests both create two rows instead of one. The failing command exits nonzero; this is the negative control, not a successful verification result.

Record what you actually observe. If the command reports an import error, zero tests or a timeout, resolve that first. Those results do not establish the expected defect.

## 3. Apply and review the smallest fix

The database must own the uniqueness invariant. In your first terminal, still in the directory where you ran the creation command (the checkout root or vault's `Labs`):

```sh
python3 -m examples.adoption.project fix /tmp/booking-starter
```

This teaching command changes only `booking.py`, and refuses if you already edited it. It changes the two `broken` defaults from `True` to `False`: initialization adds `UNIQUE(doctor, slot)` and booking stops using the deliberately broken branch. The insert catches uniqueness violations and returns 409. The tests and contracts stay intact.

Inspect `booking.py` before and after applying the fix. For a manual challenge, change those defaults yourself instead of using the command. Review every changed file, including tests: deleting an assertion is not a fix.

## 4. Verify the outcome

In the sample-project terminal, repeat:

```sh
python3 -m unittest test_booking -v
```

Expected: all three checks pass with exit code zero. Read the assertions as well as the final status. They prove response and persisted-state behavior at the Python/SQLite boundary. They do not prove an HTTP endpoint, production concurrency, authentication or interval overlap handling.

## 5. Leave an honest handoff

Edit `checkpoint.md` using your actual results. Record:

- the exact command, date, interpreter version and its result;
- changed files and whether you reviewed their diff;
- the negative-control failures and the checks passing after the fix;
- unresolved questions and the boundary not tested;
- the next command, for example rerunning the three tests in a fresh session.

Keep observed facts separate from expected behavior. Close the terminal and recover the task using only `task.md`, `proof.md` and `checkpoint.md`. Can you explain what is verified without this page?

## Transfer this to your own project

Choose one recent failure and write the same three artifacts before editing. Replace the booking invariant with your user-visible outcome. Use an isolated test fixture, seed the smallest defect, and show that your check rejects it. Then fix the defect and review the complete diff. Do not introduce seeded defects into a shared environment.

Start with one outcome and one regression if that is enough. Add a scope checker when unrelated edits become a recurring problem; add checkpoints when work crosses sessions; add independent evidence gates when self-attested completion is a risk. Use the public kit's [adoption guide](https://github.com/sakti1977/Harness-Engineering/blob/main/docs/adoption.md) for those mechanisms. Its feature ledger has a separate schema: these Markdown contracts are a lightweight learning exercise, not inputs to that validator.

## Check your understanding

1. Why is checking only the helper insufficient? **Answer:** the application may ignore its result; verify the persisted outcome.
2. Why use a database constraint? **Answer:** simultaneous requests can both pass a pre-insert availability check.
3. What stops a worker weakening these tests? **Answer:** this sample relies on developer review; it configures no protected verifier.
4. What should a failed fresh-session test do to your checkpoint? **Answer:** record the failure and investigate; the previous pass is dated evidence.

Continue with [[Project Harness Assessment]], [[Claim-to-Proof Matrix]], [[Failure to Evaluation Workflow]] and [[Cold-Session Checkpoint]]. See [[Developer Problems - Start Here]] to select another control.
