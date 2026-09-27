# Claim-to-Proof Matrix

Write the claims before the code is called done, and name how each one will be proven. A claim is covered only when a check observes the behavior **at the boundary the claim is about**. The checker reads the table below: every claim in `.harness/feature.json` needs a row, and the tested boundaries must include every required boundary. It fails once the feature asks for verification.

How to find gaps and write strong claims: [proof gaps and acceptance claims](../../../docs/proof-gaps.md). The full route behind each row: [verification routes](../../../docs/verify.md).

## Matrix: jyotish-profile-coaching

| Claim | Observation required | Required boundary | Evidence producer | Tested boundary | Gap |
| --- | --- | --- | --- | --- | --- |
| saving a profile reports synced only when the profile is stored | 200 and synced true with the profile readable from a new connection; a rejected write returns 503 and synced false | entry, persistence | `test_astro.AstroTests.test_synced_only_when_stored` | entry, persistence | None |
| age is correct for users behind and ahead of UTC | Age 48 on the eve of the birthday at UTC+5:30, UTC, UTC-5 and UTC-10 | entry, environment | `test_astro.AstroTests.test_age_correct_behind_and_ahead_of_utc` | entry, environment | None |
| coaching started before a birth-time correction is not stored against the old chart | Coaching paused after its read returns 409 once the correction lands; no coaching row written against a superseded chart | entry, persistence, concurrency | `test_astro.AstroTests.test_coaching_not_stored_against_superseded_chart` | entry, persistence, concurrency | None |
| invalid birth details are rejected and store nothing | 400, synced false and no stored profile for month 13, hour 25 and an empty date | entry, persistence | `test_astro.AstroTests.test_invalid_birth_details_store_nothing` | entry, persistence | None |

Boundaries: `unit` (a function in isolation), `entry` (the real entry point callers use: route, command, public function), `persistence` (stored state read back), `concurrency` (overlapping access to shared state), `environment` (time zone, locale or runtime settings that change the result), `external` (a real third-party or service boundary), `ui` (what a user sees).

## Evidence that does not count

These checks may be useful, but they prove none of the claims above. List them so nobody mistakes them for proof.

| Check | What it observes | Why it is not proof |
| --- | --- | --- |
| `test_save_reports_synced` | The save returns 200 and synced true | Response only. Jyotish Coach once showed a "Synced" badge while every cloud write was silently rejected; a check like this cannot tell the difference. |
| `test_age_in_ist` | Age at UTC+5:30 | One environment. Parsing a date-only string as UTC midnight never changes the date ahead of UTC, so the bug only appears behind it. |
| `test_coaching_is_generated` | Coaching returns 201 | Sequential. Nothing changes the chart during generation, so the stale write can never happen. |
| An agent's summary saying "all tests pass" | Nothing | Not an observation. Evidence is a named check run at a recorded revision. |

## Rules

- One row per claim; the claim text matches `feature.json` exactly.
- Outcome evidence supports a claim. Diagnostic evidence explains a failure. Any contradicting observation vetoes passing.
- Changing a claim, its observation, its evidence producer or the code under test invalidates earlier evidence.
- Unit tests can support a claim without proving it. For persistence, concurrency, environment, integration and external behavior, test at the real boundary with the shared state the claim depends on.
