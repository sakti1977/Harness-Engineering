# Run policy: astro-coach agent evals

This policy governs every agent run against the astro-coach fixture. It applies to the bare and harness conditions alike.

## What the agent gets
- A workspace built by `prepare_run.sh`: the product at pinned commit `43c695a`, with exactly one defect patch applied, and a fresh single-commit git history. The real history is removed, because it contains the fixing commits.
- One user report from `reports/` (held-in evidence).
- The product's own visible tests (`npm test`, `npx tsc --noEmit`).
- Coaching calls go to the local stub: `ANTHROPIC_BASE_URL=http://127.0.0.1:8787`.

## What the agent may edit
- Allowed: `app/`, `lib/`, `components/`, `supabase/migrations/`.
- Allowed: adding new test files anywhere under `lib/` or `app/`.
- Not allowed: modifying or deleting existing test files, `package.json`, `package-lock.json`, `.github/`, `.env*`, or anything under `evals/`.
  Existing tests are the judges of the work, the same rule the harness applies to its own tests.

## What the agent may run
- Allowed: `npm test`, `npx vitest`, `npx tsc --noEmit`, `npx eslint`, `npm ci`.
- Allowed: `psql` only against a local, throwaway database named with the prefix `eval_`.
- Allowed: network to `127.0.0.1` only (the stub). Package installs go through the normal registry.
- Not allowed: live Supabase or any production URL, real API keys, `git push`, deploy commands, reading `~/.ssh` or `~/.ccr`.

## Conditions
- bare: the user report, plus the editing and test rules.
- harness: bare, plus a required working method. The agent writes a plan to `HARNESS_LOG.md` before editing, logs every check it runs, and separates verified facts from suspicions in its final summary. This is a prompt-level stand-in for the kit's discipline. It does not install the kit, so a null result says little about the kit itself.

## Budget
- At most 60 minutes of wall-clock time and 100 tool calls per run.
- Each condition runs 5 times with the same defect, recorded in full.
- Driver: `run_batch.sh` runs `run_one.sh` for each defect, condition and repeat, interleaved by repeat. Each run writes `runs/<id>/` with `prepare.txt`, `prepare-commit.txt`, `agent.log` (the agent's final output), `changed.txt`, `heldout.txt`, `status` and `timing.txt`.
- Not yet recorded per run: the full list of commands the agent ran. `agent.log` holds only the final output.

## Where runs happen
- Every agent command runs through `run_sandboxed.sh`: a new network namespace (loopback only, where the stub listens), private mounts, `/home`, `/root`, `/mnt` and `/srv` hidden, environment cleared, workspace the only writable tree.
- Postgres for defect 3 runs inside the same sandbox, on a private tmpfs with a Unix socket (`checks/run-defect-03.sh`).
- The agent itself (Claude Code 2.1.332) runs inside the sandbox, so its file tools are confined too. Verified: the key file is unreadable from inside, and the sandbox has no route to the internet.
- The API key stays on the host. `relay/host_relay.py` forwards only `/v1/*` to api.anthropic.com and adds the key. Inside the sandbox the key variable holds a placeholder.

## Grading
- Held-out checks run after the agent finishes, in a fresh copy of the agent's final tree, never in the agent's workspace. Run them through `run_sandboxed.sh` with `HIDDEN_CHECKS=evals/astro-coach/checks`, which mounts the checks read-only at `/sandbox/checks`.
  - defect 1: `checks/defect-01-sync-profile-error.test.ts` (copy into `lib/` of the fresh tree; run with vitest)
  - defect 2: `checks/defect-02-age-tz.test.ts` (copy into `lib/`; run with `TZ=America/New_York`)
  - defect 3: `sh /sandbox/checks/run-defect-03.sh <migration 009 path> /sandbox/checks/defect-03-stubs.sql`
- A run counts as fixed only if its held-out check passes and no existing test was edited or deleted.
- The agent's own claim of "done" is recorded but never graded as evidence.

## Record for every run
- Condition, defect, run number, prepare_run.sh output hash, final commit hash.
- Commands run, files changed, final claim.
- Held-out result, and whether existing tests changed.
