# Verification routes

A test run proves only what it exercised. A **verification route** is the smallest run that crosses every boundary a claim depends on, written down so a fresh session can rerun it without rebuilding the journey from tests, scripts and chat history. The command is not the route: the route explains what must stay real and what must be observed, so a later rewrite cannot keep the command while quietly lowering its fidelity.

Each route below backs one claim in `.harness/feature.json` and one row of the [proof matrix](proof-matrix.md). Run all of them with:

```sh
python3 -m unittest examples.astro.test_astro -v
```

Failures name the claim, this route, what was expected, what was observed and where to repair, for example:

```text
CLAIM     coaching started before a birth-time correction is not stored against the old chart
ROUTE     docs/verify.md#route-stale-coaching
EXPECTED  coaching returns 409 and no coaching row was written against a superseded chart
OBSERVED  coaching returned 201; rows (chart_version, current_at_write): [(1, 2)]
REPAIR AT coaching write must check chart_version in the same statement (examples/astro/astro.py)
```

A red route on a broken build is the harness working: the feature stays `active`. After the fix, rerun the **same route unchanged**. Editing the route to make the build pass erases the proof target, and any edit to this file or the tests makes earlier evidence stale.

## Five fidelity checks

Compare the route's execution with the product's, not with a reassuring label such as "end-to-end":

| Check | Question | Stale-coaching route |
| --- | --- | --- |
| Entry | Does it call the same entry point real callers use? | `generate_coaching` and `save_profile`, as the API routes do |
| State | Do all actions share one store? | Coaching and the correction use the same database file |
| Timing | Does it preserve the ordering or overlap that can change the result? | Coaching pauses after its read; the correction lands; then coaching writes |
| Response | Does it assert exact visible outcomes? | 409 for the losing request, not "any status below 500" |
| Persistence | Does it read the lasting state back? | No coaching row whose chart version differs from the current one at write time |

A substitute is acceptable when it cannot change the outcome under the failure the claim names. The ephemeris stand-in stays fake here; the database cannot, because its write rules decide whether the stale write happens.

## Route: stale-coaching

| Field | Value |
| --- | --- |
| Claim | coaching started before a birth-time correction is not stored against the old chart |
| Entry | `generate_coaching()` and `save_profile()` in `examples/astro/astro.py`, from two threads |
| Boundaries | chart read, coaching composition, shared SQLite store, conditional write |
| Setup | one profile at chart version 1 (born 1977-08-15 06:30, UTC+5:30) |
| Actions | start coaching; pause it after the chart read; save the corrected birth time (07:10); release coaching |
| Observations | coaching returns 409; no row in `coaching` with `chart_version` different from `current_at_write` |
| Cleanup | temporary database deleted with its directory |

Command: `python3 -m unittest examples.astro.test_astro.AstroTests.test_coaching_not_stored_against_superseded_chart -v`

Timing coverage: `python3 -m examples.astro.sweep` injects the correction at every step of coaching generation. The broken app stores stale coaching at 11 of 13 points; a sequential run tests only the first and last, and both look fine. Route fidelity: `python3 -m examples.astro.ablation` weakens one dimension at a time and shows which weakenings let the defect ship.

## Route: profile-sync

| Field | Value |
| --- | --- |
| Claim | saving a profile reports synced only when the profile is stored |
| Entry | `save_profile()` |
| Boundaries | validation, database write and commit, the response that drives the badge |
| Setup | empty store |
| Actions | save valid birth details; then save with the write forced to fail |
| Observations | first: status 200, `synced` true, profile readable from a new connection; second: status 503, `synced` false |
| Cleanup | temporary database deleted with its directory |

Command: `python3 -m unittest examples.astro.test_astro.AstroTests.test_synced_only_when_stored -v`

## Route: age-by-timezone

| Field | Value |
| --- | --- |
| Claim | age is correct for users behind and ahead of UTC |
| Entry | `age_on()` with the stored date-only birth date |
| Boundaries | date parsing, the user's UTC offset |
| Setup | birth date 1977-08-15; local date 2026-08-14, the eve of the birthday |
| Actions | compute the age at UTC+5:30, UTC, UTC-5 and UTC-10 |
| Observations | 48 at every offset |
| Cleanup | none |

Command: `python3 -m unittest examples.astro.test_astro.AstroTests.test_age_correct_behind_and_ahead_of_utc -v`

## Route: invalid-birth-details

| Field | Value |
| --- | --- |
| Claim | invalid birth details are rejected and store nothing |
| Entry | `save_profile()` |
| Boundaries | validation, database |
| Setup | empty store |
| Actions | save month 13, hour 25 and an empty date |
| Observations | status 400, `synced` false, no stored profile each time |
| Cleanup | temporary database deleted with its directory |

Command: `python3 -m unittest examples.astro.test_astro.AstroTests.test_invalid_birth_details_store_nothing -v`

## Template

```markdown
## Route: <short-name>

| Field | Value |
| --- | --- |
| Claim | <exact claim text from .harness/feature.json> |
| Entry | <the public entry point real callers use> |
| Boundaries | <what must stay real: store, network, time zone, queue, ...> |
| Setup | <seed data and environment, including the values that matter> |
| Actions | <steps, with the ordering or concurrency that can change the result> |
| Observations | <exact responses and the lasting state read back> |
| Cleanup | <what is removed or stopped> |

Command: `<one command a fresh session can run>`
```

Add a route for every claim that crosses a process, storage, network, time-zone or timing boundary. Keep faster unit tests too: they find local regressions and explain failures with less noise. The route is the completion authority for claims whose behavior exists only across the whole journey.
