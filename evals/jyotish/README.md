# Jyotish evaluation: does the harness change what an agent delivers?

Give an agent three real-looking user reports against a small app, with and without the harness, and judge the result with checks the agent never sees.

## The task

[`task/`](task/) is a small Python and SQLite model of [Jyotish Coach](https://github.com/sakti1977/astro-coach) with three defects, reported by users in [`ISSUES.md`](task/ISSUES.md):

1. "Synced" but the profile vanished: the save never commits and swallows errors.
2. Age a day early in New York: a date-only birth date is converted from UTC.
3. Coaching saved for the old chart: a read-then-write race while a birth-time correction lands.

It ships with three weak tests that pass on the broken code.

## Conditions

| Condition | The agent gets |
| --- | --- |
| `bare` | The task only |
| `harness` | The task plus [`harness/`](harness/): a feature ledger with four claims, a proof matrix with the boundary each claim needs, one verification route per claim, an authority policy, and `AGENTS.md` with the Resume Protocol, transition gate and handoff gate. No solution code. |

## Run it

```sh
python3 evals/jyotish/prepare.py --out ~/eval-runs --condition bare --name sonnet-1
python3 evals/jyotish/prepare.py --out ~/eval-runs --condition harness --name sonnet-1
```

Each command creates a git repository for one run and prints the exact prompt to give the agent. The harness condition also gets `~/eval-runs/kit/` with only the harness scripts and schemas. Keep `--out` outside this repository, so the agent cannot find the grader.

When the agent finishes, grade the run:

```sh
python3 evals/jyotish/grade.py ~/eval-runs/harness-sonnet-1        # six hidden outcome checks
python3 evals/jyotish/regression.py ~/eval-runs/harness-sonnet-1   # would its tests catch each bug again?
```

- **`grade.py`** checks outcomes, not approach: refusing the stale write and regenerating for the new chart both pass. It also reports files changed outside scope and, for harness runs, the ledger states and the handoff result. It never modifies the run.
- **`regression.py`** runs the agent's own tests against a correct app with exactly one defect put back. A test counts only if it passes on the correct app and fails on the defective one.

`tests/test_eval_jyotish.py` keeps the grader honest in CI. It requires:

- the broken task fails exactly the three defects;
- two different correct fixes both score 6 of 6;
- each single-defect variant fails only its own check;
- grading leaves the run untouched.

## Results

- [2026-09-27 pilot with Claude models](results/2026-09-27-claude-pilot.md): Haiku 4.5, Sonnet and Opus, two runs per condition ([raw data](results/2026-09-27-claude-pilot.json)).

Results from other agents and models are welcome: open an issue with the prompt you used, the model and tool versions, and the JSON from both scripts.
