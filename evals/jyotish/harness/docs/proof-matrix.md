# Claim-to-Proof Matrix

One row per claim in `.harness/feature.json`. A claim is covered only when a check observes it at the boundary it is about. Fill the evidence producer (the test that proves it) and the boundaries that test actually observes.

| Claim | Observation required | Required boundary | Evidence producer | Tested boundary | Gap |
| --- | --- | --- | --- | --- | --- |
| saving a profile reports synced only when the profile is stored | 200 and synced true with the profile readable afterwards; a save whose write fails reports synced false and stores nothing | entry, persistence | TODO | TODO | TODO |
| age is correct for users behind and ahead of UTC | age 48 on 2026-08-14 for a 1977-08-15 birth date at UTC+5:30, UTC, UTC-5 and UTC-10 | entry, environment | TODO | TODO | TODO |
| coaching started before a birth-time correction is not stored against the old chart | after the correction to 07:10 is saved mid-generation, no coaching is stored against chart version 1 | entry, persistence, concurrency | TODO | TODO | TODO |
| invalid birth details are rejected and store nothing | 400, synced false and no stored profile for month 13, hour 25 and an empty date | entry, persistence | TODO | TODO | TODO |

Boundaries: `unit`, `entry`, `persistence`, `concurrency`, `environment`, `external`, `ui`.

## Evidence that does not count

| Check | Why it is not proof |
| --- | --- |
| `test_save_reports_synced` | Response only: it never reads the profile back |
| `test_age` | One time zone (UTC+5:30) |
| `test_coaching_is_generated` | Sequential, and it accepts 404 |
