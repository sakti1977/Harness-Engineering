# Claim-to-Proof Matrix

Write the claims before the code is called done, and name how each one will be proven. A claim is covered only when a check observes the behavior **at the boundary the claim is about**. The checker reads the table below: every claim in `.harness/feature.json` needs a row, and the tested boundaries must include every required boundary. It fails once the feature asks for verification.

How to find gaps and write strong claims: [proof gaps and acceptance claims](proof-gaps.md).

## Matrix: sample-booking

| Claim | Observation required | Required boundary | Evidence producer | Tested boundary | Gap |
| --- | --- | --- | --- | --- | --- |
| conflicting booking returns status value 409 | Second booking for the same doctor and slot returns 409 | entry | `test_booking.BookingTests.test_conflicting_booking_changes_no_rows` | entry, persistence | None |
| conflicting booking creates no persistent row | Row count is still 1 after the rejected booking | entry, persistence | `test_booking.BookingTests.test_conflicting_booking_changes_no_rows` | entry, persistence | None |
| non-conflicting booking succeeds | Different slot returns 201 and a second row is stored | entry, persistence | `test_booking.BookingTests.test_different_slot_succeeds` | entry, persistence | None |
| concurrent requests for the same slot have one winner | Two simultaneous bookings: results are [201, 409] and one row exists | entry, persistence, concurrency | `test_booking.BookingTests.test_concurrent_same_slot_has_one_winner` | entry, persistence, concurrency | None |

Boundaries: `unit` (a function in isolation), `entry` (the real entry point callers use: route, command, public function), `persistence` (stored state read back), `concurrency` (simultaneous access to shared state), `external` (a real third-party or service boundary), `ui` (what a user sees).

## Evidence that does not count

These checks may be useful for diagnosis, but they prove none of the claims above. List them so nobody mistakes them for proof.

| Check | What it observes | Why it is not proof |
| --- | --- | --- |
| `test_helper_detects_occupied_slot` | The `available()` helper reports the slot taken | Unit boundary only. The broken booking path ignores the helper, so this stays green while double bookings are stored. |
| `test_valid_booking_persists` | One booking returns 201 and stores a row | True but not a claim of this feature; it guards the happy path, not conflicts. |
| An agent's summary saying "all tests pass" | Nothing | Not an observation. Evidence is a named check run at a recorded revision. |

## Rules

- One row per claim; the claim text matches `feature.json` exactly.
- Outcome evidence supports a claim. Diagnostic evidence explains a failure. Any contradicting observation vetoes passing.
- Changing a claim, its observation, its evidence producer or the code under test invalidates earlier evidence.
- Unit tests can support a claim without proving it. For persistence, concurrency, integration and external behavior, test at the real boundary with the shared state the claim depends on.
