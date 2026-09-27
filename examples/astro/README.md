# Jyotish Coach lab

A synthetic, model-free reproduction of three defects from [Jyotish Coach](https://github.com/sakti1977/astro-coach), a Vedic astrology coaching app: it takes a user's birth details, builds their chart, and coaches behavioural and attitude changes grounded in it.

| Defect | What shipped | Weak check in this lab (green on the broken app) | Outcome check that catches it |
| --- | --- | --- | --- |
| Sync badge | The profile screen said "Synced" while no cloud write happened | `test_save_reports_synced` checks the badge only | `test_synced_only_when_stored` reads the stored profile back |
| Age behind UTC | A date-only birth date parsed as UTC midnight moved a day for users behind UTC | `test_age_in_ist` runs where the developer lives, UTC+5:30 | `test_age_correct_behind_and_ahead_of_utc` covers UTC-10 to UTC+5:30 |
| Stale coaching | Coaching generated while the user corrected their birth time was stored against the old chart | `test_coaching_is_generated` runs sequentially | `test_coaching_not_stored_against_superseded_chart` pauses coaching after its read, applies the correction, then lets it write |

The first two are real incidents recorded in the app's `NON_NEGOTIABLES.md`. The third is modelled for this lab on the app's real flow (the chart is read, an LLM call composes coaching, the result is stored).

```sh
python3 -m examples.astro.demo       # weak checks green, three claims fail, fix passes
python3 -m examples.astro.sweep      # inject the correction at every step of coaching generation
python3 -m examples.astro.ablation   # weaken the route one dimension at a time
```

Everything is standard-library Python 3.10+ with SQLite. The ephemeris is replaced by a deterministic stand-in: that substitute cannot change the outcome of any claim here, which is the test for when a fake is acceptable. The routes behind each check are written down in [docs/verify.md](../../docs/verify.md).

This is not the production app and not real astronomy. Status values resemble HTTP; there is no web server.
