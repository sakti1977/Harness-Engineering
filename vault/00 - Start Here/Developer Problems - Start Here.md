---
type: navigation
status: maintained
reviewed: 2026-10-14
---

# Developer Problems - Start Here

Choose the failure you see, then try the smallest relevant control. Reach, Power, Ground, Verdict and Carry are this vault's organizing vocabulary; you do not need to memorize them first.

## My agent says done, but the feature is broken

Run [[First Executable Harness Lab]], then complete [[Adopt One Outcome - Walkthrough]]. Start with a user-visible outcome and a regression that fails on a seeded defect. Use [[Claim-to-Proof Matrix]] when a feature makes several different claims.

## It changes unrelated files

Write [[Task Contract Template]] and [[Scope Contract]] before starting. Review the changed files against that boundary. The public kit offers a session scope checker; a document alone does not prevent writes. See [[Authority Policy]] for the permission boundary.

## A new session loses the diagnosis

Use [[Cold-Session Checkpoint]] to preserve observed results, uncertainty and one next command. Test it by handing off without the chat. Add [[Resume Replay and Fork]] only when your runtime needs replay semantics.

## Tests pass locally but the environment is wrong

Use [[Readiness Contract]] to check the actual dependencies and fixture before work. Use [[Reproducible Evaluation Environment]] when comparing runs across machines. A readiness probe does not prove the feature works.

## I cannot tell which controls are worth the effort

Use [[Project Harness Assessment]] for one recent failure. Start with [[Minimal Harness Adoption Path]]. Compare added time and caught failures; use [[Harness Ablation Experiments]] when considering removing a control.

## I want to contribute a useful improvement

Use [[Contributor Tasks]] for bounded tasks and acceptance checks. Start with one reproducible failure, one source correction or one confusing adoption step.

For deeper study, choose a route in [[Learning Path]]. Return to [[Harness Engineering - MOC]].
