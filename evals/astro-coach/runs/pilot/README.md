# Pilot run (not one of the 30 scored runs)

- Defect: 01 (sync swallows profile error), workspace from prepare_run.sh 01 (product pin 43c695a).
- Condition: bare (report text + task rules in the prompt; no harness aids).
- Model access: real model through host_relay.py; key never enters the sandbox; sandbox network is unreachable except the relay.
- Agent: Claude Code 2.1.332, --permission-mode acceptEdits, allowed Read/Edit/Write/Glob/Grep and `npx vitest run`, `npx tsc --noEmit`, max 100 turns, 3500 s timeout.
- Attempts: run1 (defect01-bare-run1.log) could not read the report (outside the agent's folder) and could not run tests (permission denied). Not counted. run2 (defect01-bare-run2.log) is the scored pilot.
- Final tree changes: M astro-coach/lib/sync-push.ts; new astro-coach/lib/sync-push-profile-error.test.ts. No existing test changed.
- Held-out check (checks/defect-01-sync-profile-error.test.ts) in a fresh copy: PASS. Agent's new test: PASS.
- Full-suite run on the graded tree: not re-run by grader (agent reports npx vitest run passes; treat as unverified until grader run).
- Caveat: n=1. The agent's own claim of "done" was not used as evidence.
