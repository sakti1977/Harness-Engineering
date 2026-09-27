---
type: case-study
status: observed-incident
reviewed: 2026-09-27
tags:
  - harness-engineering
  - case-studies
  - verdict
---

# Jyotish Coach Sync and Age Incidents

> **Evidence status:** observed incidents recorded by the app's owner in `NON_NEGOTIABLES.md` of [sakti1977/astro-coach](https://github.com/sakti1977/astro-coach), read 2026-09-27; plus an executed local reproduction in [[First Executable Harness Lab]]. The stale-coaching race in the lab is modelled on the app's flow, not a recorded incident.

## Sync badge

- Initial state: signed-in user saves a profile; the browser wrote to the database with the anon key.
- Expected versus actual: profile stored and badge "Synced"; actually every write was silently rejected by row-level security while the badge still read "Synced".
- First divergence: the write was refused because the browser session never populated the database user id.
- Control change: all profile writes go through one server-side, session-verified route; the rule is a non-negotiable with a harness test. Recorded fix: commit `4c37856`.
- Proof lesson: a response or badge check observes the entry point only. The claim needs the stored state read back.

## Age behind UTC

- Initial state: a date-only birth date string, parsed with `new Date("YYYY-MM-DD")` and read back with local getters.
- Expected versus actual: correct age everywhere; actually the date moved a day earlier for users behind UTC, giving an intermittently wrong age.
- Control change: parse date-only strings into integer parts; boundary cases in the validator tests.
- Proof lesson: a test run in one time zone proves that time zone. The claim needs the environments that change the answer.

## Dasha drift (not reproduced in the lab)

- Actual: adding fractional days to a date-only value dropped the remainder on every addition; across 729 chained additions this compounded into multi-day drift that a user reported.
- Control change: accumulate in datetime, format only at output, and a runtime consistency guard with day-exact tests.
- Proof lesson: an assertion that tolerates small errors cannot catch compounding ones. Assert exact sums.

## Reproduction

`python3 -m examples.astro.demo` reproduces the first two as synthetic models, alongside the stale-coaching race. Limits: SQLite stands in for the hosted database; there is no browser, authentication or row-level security in the lab.

## Connected concepts

- [[Claim-to-Proof Matrix]]
- [[Verification Routes and Test Fidelity]]
- [[Failure to Evaluation Workflow]]
- [[False Passing Feature]]
