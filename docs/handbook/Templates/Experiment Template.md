---
type: template
status: reusable
reviewed: 2026-09-26
---

# Harness experiment

- Status: proposed / running / completed / inconclusive.
- Hypothesis and acceptance rule: [write before running].
- Baseline and one changed mechanism: [versions/configurations].
- Tasks: [IDs, revisions, optimization/holdout split and exposure history].
- Environment: [OS, image/dependency lock, CPU/RAM, network, timeout, reset].
- Model: [provider/model ID, settings, access date; unknown details explicitly labeled].
- Budget and trials: [attempt count and total cost/time ceiling].
- Grader: [version, outcome assertions, policy checks and calibration].
- Evidence: [run IDs, commands, raw trace location and patch hashes].
- Results: [success numerator/denominator, failures, latency and cost; leave status proposed until measured].
- Decision: [adopt, reject or gather evidence, with regressions and uncertainty].

Use [Agent Evaluation Suite](../10%20-%20Harness%20Testing/Agent%20Evaluation%20Suite.md), [Grader Reliability](../10%20-%20Harness%20Testing/Grader%20Reliability.md) and [Harness Ablation Experiments](../10%20-%20Harness%20Testing/Harness%20Ablation%20Experiments.md).
