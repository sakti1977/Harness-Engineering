---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Grader Reliability

## Problem

A flawed grader can reward a broken solution or reject a correct alternative.

## Mechanism

Separate checks of final state from checks of mandatory policy. Prefer deterministic domain assertions where possible. For qualitative judgments, define a rubric, calibrate on human-reviewed examples and inspect disagreements. Protect grading data from modification by the agent under test.

## Worked example

A grader requires an exact sequence of tool calls. A different valid sequence solves the task, so the grader produces a false rejection. Conversely, a matching success phrase can earn a false acceptance while state remains wrong.

## Try it and check the result

Construct four labeled cases: correct solution, plausible but broken solution, correct alternative and ambiguous requirement. Compare the grader to the labels. Resolve ambiguity in the task rather than forcing certainty into a score.

## Tradeoffs and limits

A separate model evaluator can share the acting model’s biases. Human labels can disagree too. Publish rubric version and disagreements; do not hide them behind an aggregate score.

## Sources and interpretation

[Anthropic: agent evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) discusses grader design and calibration. [Anthropic: harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps) includes evaluator experiments.

The worked example and exercise are local teaching designs unless identified as executed in [[Vault Update Record]]. Source findings do not establish that this design is best for every project.

## Connected concepts

- [[Claim-to-Proof Matrix]]
- [[Agent Evaluation Suite]]
- [[First Executable Harness Lab]]
