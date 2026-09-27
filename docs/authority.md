# Authority Policy

**Default: deny.** Anything this policy does not allow is refused. The agent may *request* an action; the harness decides whether this session may perform it. Capability and permission are separate.

This file has three parts:

1. **The policy** for this starter's Jyotish Coach example, with guidance under each section.
2. **Where each rule is enforced.** An instruction file alone enforces nothing.
3. **A blank, commented template** to copy into your own project.

**How to adopt it:** copy the blank template, fill each section for one project, and keep it next to `.harness/feature.json`. Review it whenever the feature's `expected_surface` changes. The agent reads this file through your instruction file (`.github/copilot-instructions.md`, `CLAUDE.md` or `AGENTS.md`). Where the two disagree, the stricter rule wins.

---

## Read

- allowed: `examples/**`, `tests/**`, `docs/**`, `README.md`, `.harness/*`
- denied: `.env`, `.env.*`, `**/*.pem`, `**/*.key`, `secrets/**`, `~/.ssh/**`, `~/.aws/**`

> **Guidance.** Reading is not harmless: anything the agent reads can end up in its context, traces, checkpoints and pull request descriptions. List secret locations explicitly, even inside allowed folders. **Deny beats allow**, so `.env` stays denied even though it sits in the project root.
>
> **Weak:** `allowed: everything`. **Better:** the source, test and doc folders the task needs.

## Write

- allowed: `examples/astro/astro.py`, `examples/astro/test_astro.py`, `.harness/checkpoint.md`
- denied:
  - ledger: `.harness/feature.json`, `.harness/feature-log.jsonl` (state changes only through `scripts/harness_transition.py`)
  - evidence: `.harness/evidence.json` (written by the verifier or CI, not the worker)
  - policy: `docs/authority.md`, `docs/scope-contract.md`, `.github/copilot-instructions.md`, `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, `.github/CODEOWNERS`
  - verification config: `.github/workflows/**`, `scripts/harness_check.py`, `schemas/**`, test runner config

> **Guidance.** Keep `allowed` identical to `expected_surface` in `.harness/feature.json`, plus the checkpoint. Then `python3 scripts/harness_check.py --session` catches any write outside it.
>
> Protect the files that judge the work. An agent that can edit its own policy, ledger or CI can widen its authority or mark itself done. Tests are the subtle case: adding a test inside the surface is fine, but weakening or deleting an existing assertion needs human review.
>
> **Weak:** `allowed: src/**`. **Better:** the two or three files this feature changes.

## Commands

- allowed (exact strings):
  - `python3 -m unittest examples.astro.test_astro -v`
  - `python3 -m examples.astro.demo`
  - `python3 -m examples.astro.sweep`
  - `python3 scripts/harness_check.py --session`
  - `git status`, `git diff`, `git log --oneline -20`
- denied by default: everything else, including `pip install`, `curl`, `rm -rf`, `git push`, `git reset --hard` and database reset scripts

> **Guidance.** List exact commands, not prefixes. `python3 *` also allows `python3 -c "anything"`, which is no policy at all. Judge the target and the consequence, not how scary the command looks: `db:reset` against a disposable test database can be fine, while the same command against a shared database is destructive.
>
> When the agent needs a command that is not listed, it asks for a grant (below). It never tries a different command that achieves the same effect.

## Secrets

- injected as: none needed for this starter. For the real app, for example: `EPHEMERIS_SHARED_SECRET`, `ANTHROPIC_API_KEY` (sandbox or test values only)
- never printed: every injected variable, plus anything matching `*_TOKEN`, `*_KEY`, `*_SECRET`, `*PASSWORD*`
- redact on: trace, checkpoint, failure packet, exit report (write `[REDACTED:VARIABLE_NAME]`)

> **Guidance.** This file lists variable **names**, never values. The agent uses a secret by reference (`$TEST_DATABASE_URL`), never by echoing it, printing the environment or writing it into a file. Inject sandbox or test credentials only; production credentials never enter an agent session.
>
> Redaction must happen before anything is written. A checkpoint containing a token is a leak even if nobody reads it.

## Requires approval

| Action | Example in this project | Why it needs a human |
| --- | --- | --- |
| Schema change | Adding a column to `coaching` or a new Supabase migration | Hard to reverse; affects other features |
| Destructive store operation | Deleting rows, dropping tables, resetting a database | Data loss if the target is wrong |
| History rewrite | `git rebase`, `git push --force`, amending shared commits | Erases other people's work and the audit trail |
| Dependency install | `pip install freezegun` | Supply-chain risk; changes the environment for everyone |
| Publish | Tagging a release, deploying, publishing a package | Visible outside the team |
| Outbound message to a person | Push notifications to users, email, issue or pull request comments | Speaks for the product or the team |

> **Guidance.** An approval request names one action, one resource and the reason, then waits. "Can I clean up the database?" is not approvable; "Delete the 2 coaching rows for `user-1` in the local lab database, to rerun the stale-coaching route" is.

## Grants

- scope: one action, one resource, one session
- recorded: in the **Grants** section of `.harness/checkpoint.md`
- expiry: the end of the session; nothing carries over to the next one

Example record:

```text
G-1 | 2026-09-27 14:05 IST | approved by: sakti
action:   pip install freezegun==1.5.1
resource: local virtual environment only
session:  ASTRO-1, session 4
reason:   freeze the clock in the birthday-eve age test
expires:  end of session
```

> **Guidance.** There are no standing grants. The agent cannot grant itself anything, and a grant for one action does not stretch to similar ones: approval for `freezegun` does not cover `requests`. If a grant is needed in every session, change the policy in a reviewed commit instead.

## Refusal codes

When the agent declines or is blocked, it reports one of these codes, the exact action, and the grant that would allow it:

- `SECRET_PATH_DENIED`: a read or print that would expose a secret
- `PATH_OUTSIDE_SURFACE`: a write outside the allowed paths
- `PROTECTED_FILE_DENIED`: a write to the ledger, evidence, policy or verification config
- `COMMAND_NOT_ALLOWED`: a command not on the exact list
- `DESTRUCTIVE_ACTION_REQUIRES_APPROVAL`: anything in the approval table

```text
COMMAND_NOT_ALLOWED: pip install freezegun==1.5.1
Needed for: freezing the clock in test_age_correct_behind_and_ahead_of_utc
Grant requested: one install into the local venv, this session only
```

---

## Where each rule is enforced

This file states the policy; tools enforce it. Record what enforces each rule in your project so nobody mistakes guidance for a control.

| Rule | Guidance only | Real enforcement |
| --- | --- | --- |
| Read denials | Instruction file | Your agent tool's permission deny rules (for example `permissions.deny` in Claude Code's `.claude/settings.json`); keep secrets out of the workspace |
| Write scope | Instruction file | `harness_check.py --session` after the fact; tool permission rules during the session |
| Protected files | Instruction file | CODEOWNERS and branch protection; the transition log's replay checks |
| Commands | Instruction file | Tool allow lists with exact commands; sandboxed or containerised runners |
| Secrets | Instruction file | Inject only sandbox credentials; CI secret masking |
| Approvals and grants | Instruction file and checkpoint | Human review before merge; no production credentials in the session |

---

## Blank template (copy this)

```markdown
# Authority Policy
# Default: deny. Anything not allowed below is refused.
# The agent may request an action; the harness decides. Stricter rule wins.

## Read
# Folders the task needs. Deny beats allow, so list secrets even inside allowed folders.
- allowed: <source_globs>, <test_globs>, <docs_globs>
- denied: <secret_files>          # .env, .env.*, *.pem, *.key, secrets/**

## Write
# Keep "allowed" identical to expected_surface in .harness/feature.json.
- allowed: <in_scope_globs>, .harness/checkpoint.md
- denied: <ledger_file>           # .harness/feature.json, .harness/feature-log.jsonl
          <evidence_file>         # .harness/evidence.json (verifier or CI only)
          <policy_file>           # this file, instruction files, tool settings, CODEOWNERS
          <verification_config>   # CI workflows, test config, checker scripts

## Commands
# Exact strings, not prefixes. "python3 *" is not a policy.
- allowed: <exact_command_list>
- denied by default: everything else

## Secrets
# Names only, never values. Sandbox or test credentials only.
- injected as: <variable_names>
- never printed: <variable_names>, *_TOKEN, *_KEY, *_SECRET
- redact on: trace, checkpoint, failure packet, exit report

## Requires approval
# One action, one resource, one reason per request.
- schema change, destructive store operation, history rewrite,
  dependency install, publish, outbound message to a person

## Grants
# No standing grants. Record each one in .harness/checkpoint.md.
- one action, one resource, one session, recorded

## Enforced by
# What actually stops each rule being broken (tool settings, CODEOWNERS, CI).
- read: <mechanism>
- write: <mechanism>
- commands: <mechanism>
```
