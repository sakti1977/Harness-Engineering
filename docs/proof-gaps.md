# Proof gaps and acceptance claims

A **proof gap** is the distance between what a check observes and what a claim says. Coding agents fall into proof gaps because "tests pass" is the cheapest signal available: a green helper test looks exactly like a green outcome test in a summary. This guide covers how to write claims that can be proven, how to audit existing checks for gaps, and how the harness enforces the result.

Try it first: `python3 -m examples.booking.demo` shows a real proof gap. A helper test stays green while the application stores double bookings.

## 1. Write acceptance claims that can be proven

Start from the one-line outcome in `.harness/feature.json`, then turn it into claims. A claim is one observable behavior, with a specific value, at a named boundary.

### Claim checklist

Ask each question of the outcome. Keep the claims that matter for this feature and write down why you dropped the others.

| Question | Claim it produces | Booking example |
| --- | --- | --- |
| What happens on success? | Result and stored effect | Different slot returns 201 and a second row is stored |
| What must be refused? | Rejection value | Conflicting booking returns 409 |
| What must *not* happen on refusal or failure? | No side effect | Conflicting booking creates no persistent row |
| What happens with invalid input? | Validation result and no side effect | Empty doctor returns 400 and stores no row |
| What if two things happen at once? | Ordering or single-winner rule | Two simultaneous bookings for one slot: one 201, one 409, one row |
| What if it happens twice? | Idempotency or duplicate handling | A retried request with the same key stores one row |
| Who is allowed? | Permission rule | A patient cannot book on another patient's behalf |
| What leaves the system? | External effect, observed at the real boundary | One confirmation message is queued per booking |
| What must keep working? | Regression claim | Existing bookings for other doctors are unchanged |

The booking lab implements the first five rows; the rest show how the checklist extends to a real service.

### Rules for a good claim

1. **Observable:** it names something a check can see (a response, a stored row, a message), not an intention ("handles conflicts").
2. **Specific:** it states the value (409, one row), not a quality ("correctly").
3. **One behavior:** "returns 409 and stores no row" is two claims, because a test can prove one without the other.
4. **Boundary named:** it says whether it is about the entry point, stored state, concurrency or an external system.
5. **Falsifiable:** a plausible broken implementation must fail it. If you cannot imagine the broken version, the claim is too vague.

### Weak to strong

| Weak claim | Why it is weak | Strong claim(s) |
| --- | --- | --- |
| Booking works | Not observable; no value | Different slot returns 201 and a second row is stored |
| Handles conflicts | Two behaviors, no values | Conflicting booking returns 409 · Conflicting booking creates no persistent row |
| Is thread-safe | Not observable as stated | Two simultaneous bookings for one slot produce results [201, 409] and one row |
| Validates input | Which input? What result? | Empty doctor returns 400 and stores no row |
| Sends a confirmation | Boundary unclear; a mock would pass | One confirmation is accepted by the message queue per successful booking (external) |
| Is fast | No number, no conditions | 100 sequential bookings on the test fixture complete in under 2 seconds (entry) |
| Tests pass | Evidence, not a claim | Replace with the claims those tests are supposed to prove |

## 2. Find proof gaps

### Gap types

| Gap | Symptom | Question to ask | Booking example |
| --- | --- | --- | --- |
| **Boundary** | The test calls a helper, not the entry point callers use | Does this check go through the same path as a real caller? | `test_helper_detects_occupied_slot` checks `available()`, which the broken `book()` ignores |
| **State** | The test checks the response, not what was stored | After the action, does the check read the stored state back? | A test asserting 409 alone misses a row stored before the error |
| **Negative** | Only the happy path is tested | Is there a check for what must be refused and what must not change? | Only testing that a valid booking returns 201 |
| **Timing** | A concurrency claim tested one call at a time | Do the calls actually overlap, sharing the same state? | Two sequential bookings pass; two simultaneous ones both insert |
| **Fidelity** | Mocks, fakes or an in-memory store stand in for the real thing | Would the real database, service or network behave the same? | A dict-based fake has no uniqueness constraint to violate |
| **Oracle** | The assertion is too weak to fail | Could a broken result still satisfy this assertion? | `assertIn(status, (201, 409))`, or "no exception raised" |
| **Staleness** | Evidence is older than the code or the claim | Was this evidence recorded after the last change? | Tests ran before the agent's final edit |
| **Attribution** | Evidence is a statement, not an observation | Which named check, at which revision, produced this result? | "All tests pass" in an agent's summary |

### Audit steps

1. **List the claims** from `.harness/feature.json`.
2. **Write the required boundary** for each claim: `unit`, `entry`, `persistence`, `concurrency`, `external` or `ui`.
3. **Read each existing check's assertions**, not its name, and write down what it actually observes. A test called `test_conflict` that only calls a helper observes `unit`.
4. **Fill the proof matrix** in `docs/proof-matrix.md`. Any required boundary missing from the tested boundary is a gap, and so is a claim with no row.
5. **Seed a plausible broken version** and run the producers against it, as the booking lab does. At least one producer per claim must fail. If every check stays green, you have a gap the matrix did not reveal: the oracle is too weak or the test does not reach the boundary it claims.
6. **Close each gap** with a check at the right boundary. Show it failing on the broken version and passing on the fix, then record the evidence.

### Worked example: the booking lab

Before the fix, the only conflict check was the helper test. Written honestly, the matrix looks like this:

| Claim | Observation required | Required boundary | Evidence producer | Tested boundary | Gap |
| --- | --- | --- | --- | --- | --- |
| conflicting booking returns status value 409 | Second booking returns 409 | entry | `test_helper_detects_occupied_slot` | unit | |
| conflicting booking creates no persistent row | Row count stays 1 | entry, persistence | `test_helper_detects_occupied_slot` | unit | |
| non-conflicting booking succeeds | 201 and a second row | entry, persistence | `test_different_slot_succeeds` | entry, persistence | |

With the feature at `ready_for_verification`, the checker reports:

```text
FAIL PROOF_BOUNDARY_GAP docs/proof-matrix.md
  conflicting booking returns status value 409: needs entry but test_helper_detects_occupied_slot only observes unit; missing entry.
FAIL PROOF_BOUNDARY_GAP docs/proof-matrix.md
  conflicting booking creates no persistent row: needs entry, persistence but test_helper_detects_occupied_slot only observes unit; missing entry, persistence.
PASS PROOF_COVERED
FAIL PROOF_CLAIM_MISSING docs/proof-matrix.md
  No proof-matrix row for: concurrent requests for the same slot have one winner
```

Closing the gaps takes checks at the right boundary: `test_conflicting_booking_changes_no_rows` goes through `book()` and then reads the row count, and `test_concurrent_same_slot_has_one_winner` releases two threads together with a barrier against one database file. The lab runs both against each variant: they fail on the broken one and pass on the fix. The [completed matrix](proof-matrix.md) shows the result, and keeps the helper test in its "does not count" table.

## 3. What the harness enforces

| Stage | Check | Command |
| --- | --- | --- |
| While working | Missing rows and boundary gaps are reported as INFO | `python3 scripts/harness_check.py` |
| Asking for verification | `active -> ready_for_verification` is refused until every claim has a row, a producer and no boundary gap | `python3 scripts/harness_transition.py --to ready_for_verification ...` |
| Approving | `passing` needs passing evidence for every claim, recorded after the last code change, from an independent verifier | `python3 scripts/harness_transition.py --to passing ...` |
| After approval | Changing a claim or the verified code marks `passing` stale | `python3 scripts/harness_check.py` |

Checker codes: `PROOF_MATRIX_NO_TABLE`, `PROOF_CLAIM_MISSING`, `PROOF_UNKNOWN_CLAIM` (a row whose claim is not in the ledger, usually reworded), `PROOF_PRODUCER_MISSING`, `PROOF_BOUNDARY_UNKNOWN`, `PROOF_BOUNDARY_GAP`.

## Limits

- The checker trusts the **Tested boundary** column as written; it does not read your tests. A reviewer must check that column against the assertions, and step 5 of the audit is the real test.
- Boundaries are coarse. `persistence` does not say *which* state was read back; the Observation column must.
- A covered matrix means every claim has a plausible route to proof. It does not mean the claims are the right ones: use the checklist, and have someone other than the author review them.
