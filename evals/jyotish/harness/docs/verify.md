# Verification routes

A test run proves only what it exercised. Each route is the smallest run that crosses every boundary its claim depends on. Write a test that follows each route, confirm it fails on the current code, then fix the code.

## Route: profile-sync

| Field | Value |
| --- | --- |
| Claim | saving a profile reports synced only when the profile is stored |
| Entry | `save_profile()` |
| Boundaries | validation, database write, the response that drives the badge |
| Setup | empty database |
| Actions | save valid birth details; then save with the database write failing |
| Observations | 200 and synced true with the profile readable afterwards; a save whose write fails reports synced false and stores nothing |
| Cleanup | temporary database removed |

Command: `TODO`

## Route: age-by-timezone

| Field | Value |
| --- | --- |
| Claim | age is correct for users behind and ahead of UTC |
| Entry | `age_on()` |
| Boundaries | date parsing, the user's UTC offset |
| Setup | birth date 1977-08-15; local date 2026-08-14 (the eve of the birthday) |
| Actions | compute the age at UTC+5:30, UTC, UTC-5 and UTC-10 |
| Observations | age 48 on 2026-08-14 for a 1977-08-15 birth date at UTC+5:30, UTC, UTC-5 and UTC-10 |
| Cleanup | temporary database removed |

Command: `TODO`

## Route: stale-coaching

| Field | Value |
| --- | --- |
| Claim | coaching started before a birth-time correction is not stored against the old chart |
| Entry | `generate_coaching()` and `save_profile()` |
| Boundaries | profile read, coaching composition, shared SQLite database, coaching write |
| Setup | one profile born 1977-08-15 06:30 at UTC+5:30 (chart version 1) |
| Actions | start coaching; after it has read the profile and before it stores coaching, save the corrected birth time 07:10; let coaching finish |
| Observations | after the correction to 07:10 is saved mid-generation, no coaching is stored against chart version 1 |
| Cleanup | temporary database removed |

Command: `TODO`

## Route: invalid-birth-details

| Field | Value |
| --- | --- |
| Claim | invalid birth details are rejected and store nothing |
| Entry | `save_profile()` |
| Boundaries | validation, database |
| Setup | empty database |
| Actions | save month 13, hour 25 and an empty date |
| Observations | 400, synced false and no stored profile for month 13, hour 25 and an empty date |
| Cleanup | temporary database removed |

Command: `TODO`
