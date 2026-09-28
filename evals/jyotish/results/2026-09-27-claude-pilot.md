# Pilot, 2026-09-27: Claude Haiku 4.5, Sonnet and Opus

**On this three-bug task, the harness took Haiku 4.5 from 4–5 of 6 hidden checks, with both runs reporting everything fixed, to 6 of 6 with accurate reports. It also gave every harness run a test that catches the race if it comes back. Sonnet and Opus fixed everything either way.** This is a pilot: two runs per cell, Claude models only.

| Model | Condition | Hidden checks (run 1, run 2) | Test catches the race if reintroduced | Reported "all fixed" while a check failed | Avg tokens | Avg tool calls | Avg minutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Haiku 4.5 | bare | 4, 5 | 0 of 2 | 2 of 2 | 85,546 | 17.5 | 2.7 |
| Haiku 4.5 | harness | 6, 6 | 2 of 2 | 0 of 2 | 105,474 | 46 | 3.9 |
| Sonnet | bare | 6, 6 | 1 of 2 | 0 of 2 | 104,757 | 15.5 | 1.7 |
| Sonnet | harness | 6, 6 | 2 of 2 | 0 of 2 | 130,751 | 42 | 3.1 |
| Opus | bare | 6, 6 | 2 of 2 | 0 of 2 | 90,454 | 4.5 | 0.7 |
| Opus | harness | 6, 6 | 2 of 2 | 0 of 2 | 107,130 | 13.5 | 1.8 |

Across all 12 runs, no file was changed outside scope. In the harness runs:

- every run reached `ready_for_verification`, and none tried to mark the feature `passing` or wrote the verifier's evidence file;
- five of six passed the handoff gate;
- the sixth (Haiku, run 1) wrote its checkpoint before changing state, and the gate reported it stale.

## What the misses looked like

Without the harness, both Haiku runs fixed the sync and age bugs and missed the race.

- **Run 1** decided the race was a symptom of the sync bug. It also still swallowed write errors, so a failed save still showed "Synced".
- **Run 2** filtered stale coaching out of the read path but still stored it, so the user still received guidance for the old chart.

One Sonnet run without the harness fixed the race but wrote no test that fails if it returns.

## Cost

With the harness, runs used 1.2–1.25× the tokens, 2.6–3.0× the tool calls and 1.4–2.5× the wall-clock time. For Opus, the harness bought an audit trail and route-shaped tests rather than correctness.

## Limits

- **Two runs per cell.** Treat the differences as signals to test with more runs, not as rates.
- **Claude models only.** Other vendors' tools read different instruction files and enforce permissions differently.
- **The harness condition carries more information:** its claims and routes spell out what "fixed" means. This measures the harness as a whole; it does not say which part helped.
- **One small task, written by the same author** as the harness and the grader.
- **Isolation by instruction only.** Agents were told to stay in their directory; no sandbox enforced it.
- **Three evaluation bugs were found and fixed while running it.** The grader's race check depended on the sync fix, and was isolated. The weak-test runner used a path `unittest` cannot import. Grading wrote bytecode into the run directories, making checkpoints look stale; grading is now read-only. The grader was validated against the broken app and two different correct fixes before any agent ran. The pilot's task repository also committed `__pycache__` files; the current `task/` ignores them.

Per-run grades, regression results and agent-reported usage are in the [raw data](2026-09-27-claude-pilot.json).
