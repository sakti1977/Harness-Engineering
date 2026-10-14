---
type: navigation
status: maintained
reviewed: 2026-10-14
---

# Developer Problems - Start Here

Choose the failure you see, then try the smallest relevant control. Reach, Power, Ground, Verdict and Carry are this vault's organizing vocabulary; you do not need to memorize them first.

## My agent says done, but the feature is broken

Run [First Executable Harness Lab](../11%20-%20Practical%20Implementations/First%20Executable%20Harness%20Lab.md), then complete [Adopt One Outcome - Walkthrough](../11%20-%20Practical%20Implementations/Adopt%20One%20Outcome%20-%20Walkthrough.md). Start with a user-visible outcome and a regression that fails on a seeded defect. Use [Claim-to-Proof Matrix](../06%20-%20Verdict/Claim-to-Proof%20Matrix.md) when a feature makes several different claims.

## It changes unrelated files

Write [Task Contract Template](../Templates/Task%20Contract%20Template.md) and [Scope Contract](../05%20-%20Scope/Scope%20Contract.md) before starting. Review the changed files against that boundary. The public kit offers a session scope checker; a document alone does not prevent writes. See [Authority Policy](../03%20-%20Power/Authority%20Policy.md) for the permission boundary.

## A new session loses the diagnosis

Use [Cold-Session Checkpoint](../07%20-%20Carry/Cold-Session%20Checkpoint.md) to preserve observed results, uncertainty and one next command. Test it by handing off without the chat. Add [Resume Replay and Fork](../07%20-%20Carry/Resume%20Replay%20and%20Fork.md) only when your runtime needs replay semantics.

## Tests pass locally but the environment is wrong

Use [Readiness Contract](../04%20-%20Ground/Readiness%20Contract.md) to check the actual dependencies and fixture before work. Use [Reproducible Evaluation Environment](../04%20-%20Ground/Reproducible%20Evaluation%20Environment.md) when comparing runs across machines. A readiness probe does not prove the feature works.

## I cannot tell which controls are worth the effort

Use [Project Harness Assessment](../11%20-%20Practical%20Implementations/Project%20Harness%20Assessment.md) for one recent failure. Start with [Minimal Harness Adoption Path](../11%20-%20Practical%20Implementations/Minimal%20Harness%20Adoption%20Path.md). Compare added time and caught failures; use [Harness Ablation Experiments](../10%20-%20Harness%20Testing/Harness%20Ablation%20Experiments.md) when considering removing a control.

## I want to contribute a useful improvement

Use [Contributor Tasks](Contributor%20Tasks.md) for bounded tasks and acceptance checks. Start with one reproducible failure, one source correction or one confusing adoption step.

For deeper study, choose a route in [Learning Path](Learning%20Path.md). Return to [Harness Engineering - MOC](Harness%20Engineering%20-%20MOC.md).
