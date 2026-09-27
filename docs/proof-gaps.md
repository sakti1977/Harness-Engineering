# Proof gaps and acceptance claims

A **proof gap** is the distance between what a check observes and what a claim says. Coding agents fall into proof gaps because "tests pass" is the cheapest signal available: a green response check looks exactly like a green outcome check in a summary. This guide covers how to write claims that can be proven, how to audit existing checks for gaps, and how the harness enforces the result.

The running example is [Jyotish Coach](https://github.com/sakti1977/astro-coach), a Vedic astrology app that takes a user's birth details, builds their chart and coaches behavioural and attitude changes grounded in it. Try it first: `python3 -m examples.astro.demo` shows three weak checks staying green while the app loses profile writes, gets ages wrong behind UTC and stores coaching against a chart the user has already corrected.

## 1. Write acceptance claims that can be proven

Start from the one-line outcome in `.harness/feature.json`, then turn it into claims. A claim is one observable behavior, with a specific value, at a named boundary.

### Claim checklist

Ask each question of the outcome. Keep the claims that matter for this feature and write down why you dropped the others.

| Question | Claim it produces | Jyotish Coach example |
| --- | --- | --- |
| What happens on success? | Result and stored effect | Saving a profile returns synced true and the profile can be read back |
| What must be refused? | Rejection value | Coaching for a chart that changed mid-generation returns 409 |
| What must *not* happen on refusal or failure? | No side effect | A rejected write reports synced false, never "Synced" |
| What happens with invalid input? | Validation result and no side effect | Month 13 returns 400 and stores nothing |
| What if two things happen at once? | Ordering rule | Coaching started before a birth-time correction is not stored against the old chart |
| Where does the environment change the answer? | Result per environment | Age is 48 on the eve of the birthday at UTC+5:30, UTC, UTC-5 and UTC-10 |
| What if it happens twice? | Idempotency or duplicate handling | Saving the same profile from two tabs keeps one profile |
| Who is allowed? | Permission rule | A signed-in user can read and write only their own profile |
| What leaves the system? | External effect, observed at the real boundary | The ephemeris service rejects a request without the shared secret |
| What must keep working? | Regression claim | Every remedy still includes a behavioural practice |

The lab implements the first six rows. The rest show how the checklist extends to the real app; several come straight from its `NON_NEGOTIABLES.md`.

### Rules for a good claim

1. **Observable:** it names something a check can see (a response, a stored row, a computed value), not an intention ("sync works").
2. **Specific:** it states the value (409, age 48), not a quality ("correctly").
3. **One behavior:** "reports synced and stores the profile" is two observations; a test can prove one without the other.
4. **Boundary named:** it says whether it is about the entry point, stored state, concurrency, the environment or an external system.
5. **Falsifiable:** a plausible broken implementation must fail it. If you cannot imagine the broken version, the claim is too vague.

### Weak to strong

| Weak claim | Why it is weak | Strong claim(s) |
| --- | --- | --- |
| Cloud sync works | Not observable; the badge can lie | Saving a profile returns synced true and the profile is readable from a new connection · A rejected write returns synced false |
| Age is calculated correctly | Which users? Which dates? | Age is 48 on 2026-08-14 for a 1977-08-15 birth date at UTC+5:30, UTC, UTC-5 and UTC-10 |
| Coaching stays in sync with the chart | Not observable as stated | Coaching started before a birth-time correction returns 409 and stores no row against the old chart |
| Validates birth details | Which input? What result? | Month 13, hour 25 and an empty date each return 400 and store nothing |
| Coaching is grounded | Grounded in what? | Every coaching line names a placement present in the user's chart |
| Dasha dates are accurate | No tolerance, no level | Each dasha level's sub-periods sum in days exactly to the parent span, with no gaps or overlaps |
| Tests pass | Evidence, not a claim | Replace with the claims those tests are supposed to prove |

## 2. Find proof gaps

### Gap types

| Gap | Symptom | Question to ask | Jyotish Coach example |
| --- | --- | --- | --- |
| **Boundary** | The test calls a helper, not the entry point callers use | Does this check go through the same path as a real caller? | Testing the chart helper while the API route reads a different field |
| **State** | The test checks the response, not what was stored | After the action, does the check read the stored state back? | The "Synced" badge: the response said synced while every write was rejected |
| **Environment** | The test runs in one time zone, locale or configuration | Would a user elsewhere get a different answer? | Ages right in IST, a day early behind UTC |
| **Negative** | Only the happy path is tested | Is there a check for what must be refused and what must not change? | Only testing that a valid profile saves |
| **Timing** | An ordering claim tested one call at a time | Do the actions actually overlap, sharing the same state? | Sequential coaching never sees the birth-time correction |
| **Fidelity** | Mocks, fakes or an in-memory store stand in for the real thing | Could this substitute change the outcome under the failure the claim names? | A per-test store gives coaching and the correction separate databases, so they never collide |
| **Oracle** | The assertion is too weak to fail | Could a broken result still satisfy this assertion? | Accepting any status below 500; a dasha test that allows a day of drift |
| **Staleness** | Evidence is older than the code or the claim | Was this evidence recorded after the last change? | Tests ran before the agent's final edit |
| **Attribution** | Evidence is a statement, not an observation | Which named check, at which revision, produced this result? | "All tests pass" in an agent's summary |

### Audit steps

1. **List the claims** from `.harness/feature.json`.
2. **Write the required boundary** for each claim: `unit`, `entry`, `persistence`, `concurrency`, `environment`, `external` or `ui`.
3. **Read each existing check's assertions**, not its name, and write down what it actually observes. A test called `test_sync` that only reads the response observes `entry`, not `persistence`.
4. **Fill the proof matrix** in `docs/proof-matrix.md`. Any required boundary missing from the tested boundary is a gap, and so is a claim with no row.
5. **Seed a plausible broken version** and run the producers against it, as the lab does. At least one producer per claim must fail. If every check stays green, you have a gap the matrix did not reveal: the oracle is too weak or the test does not reach the boundary it claims.
6. **Close each gap** with a check at the right boundary, and write its [verification route](verify.md). Show it failing on the broken version and passing on the fix, then record the evidence.

### Worked example: Jyotish Coach

Suppose the only checks were the three weak ones. Written honestly, the matrix looks like this:

| Claim | Observation required | Required boundary | Evidence producer | Tested boundary | Gap |
| --- | --- | --- | --- | --- | --- |
| saving a profile reports synced only when the profile is stored | synced true and the profile stored | entry, persistence | `test_save_reports_synced` | entry | |
| age is correct for users behind and ahead of UTC | Age 48 at every offset | entry, environment | `test_age_in_ist` | entry | |
| invalid birth details are rejected and store nothing | 400 and nothing stored | entry, persistence | `test_invalid_birth_details_store_nothing` | entry, persistence | |

With the feature at `ready_for_verification`, the checker reports:

```text
FAIL PROOF_BOUNDARY_GAP docs/proof-matrix.md
  saving a profile reports synced only when the profile is stored: needs entry, persistence but test_save_reports_synced only observes entry; missing persistence.
FAIL PROOF_BOUNDARY_GAP docs/proof-matrix.md
  age is correct for users behind and ahead of UTC: needs entry, environment but test_age_in_ist only observes entry; missing environment.
FAIL PROOF_CLAIM_MISSING docs/proof-matrix.md
  No proof-matrix row for: coaching started before a birth-time correction is not stored against the old chart
PASS PROOF_COVERED
```

Closing the gaps takes checks at the right boundary:

- `test_synced_only_when_stored` reads the profile back from a new connection and forces a rejected write.
- `test_age_correct_behind_and_ahead_of_utc` runs the eve-of-birthday case at four offsets.
- `test_coaching_not_stored_against_superseded_chart` pauses coaching after its read, applies the correction, then lets it write.

The lab runs all three against each variant: they fail on the broken one and pass on the fix. The [completed matrix](proof-matrix.md) shows the result, and keeps the weak checks in its "does not count" table.

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
- Boundaries are coarse. `persistence` does not say *which* state was read back; the Observation column and the [verification route](verify.md) must.
- A covered matrix means every claim has a plausible route to proof. It does not mean the claims are the right ones: use the checklist, and have someone other than the author review them.
