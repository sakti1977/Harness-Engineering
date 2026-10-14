# Try the harness on one bug

We want to learn where the instructions work and where they get in your way. Incomplete attempts are useful feedback. This is not a test of your ability.

You need Python 3.10+, a terminal and a disposable copy or branch of a project with one reproducible bug. The walkthrough needs no model key or package installation. Your own project's setup may differ; record that effort separately.

## Before starting

The maintainer will give you one repository revision. Clone the repository, check out that revision, and record your platform, Python version and the revision. Start timing when you first open this guide, including setup time; note any breaks.

Use your normal tools and public documentation. Record any AI assistance or help from another person. For the first attempt, try following the instructions without maintainer coaching. If you get stuck or want to stop, record the step and what you expected; you can request help afterward.

## Phase A — the filled example, up to 30 minutes

Open the [minimal adoption walkthrough](../handbook/11%20-%20Practical%20Implementations/Adopt%20One%20Outcome%20-%20Walkthrough.md) and follow it through the handoff. In a GitHub checkout, run its modules from the repository root; use `Labs` only in a standalone vault copy.

Keep the actual test output and your checkpoint. Tell the observer when you first have a result you find useful, and explain why. At the end, explain what the tests prove and what remains outside their scope.

## Phase B — your own bug, up to 45 minutes

In your disposable project copy, use the walkthrough's transfer step:

1. Choose one reproducible bug and describe the outcome a user should see.
2. State the files the change may touch and what is outside its scope.
3. Create or identify one regression that fails for that bug at the relevant boundary. Keep the assertion intact if you try a fix.
4. Write a checkpoint containing the actual command/result, changed files, limits and next action.

Use the smallest controls that help. The full feature ledger and installer are optional in this phase. If you choose them, note the extra time and any confusing steps. You do not need to fix the whole bug to provide useful feedback.

If no suitable bug or runnable project is available, say so; phase B can remain not attempted. Keep private project data local and share only the excerpts you agree to share.

## Debrief

Return the [feedback template](feedback-template.md) through the channel agreed with the maintainer. Include the first confusing instruction, any help you needed, the first useful result, and whether you would use this approach again. You may leave details unknown; please do not guess measurements.

An optional seven-day follow-up asks whether you actually reused any part of the approach. Tell the maintainer whether you want that follow-up.
