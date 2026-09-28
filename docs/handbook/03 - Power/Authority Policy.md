---
type: concept
status: maintained
reviewed: 2026-09-28
provenance: inherited teaching material, rewritten around this repository's executable examples
tags:
  - harness-engineering
  - power
---

# Authority Policy

## Problem

Scope says which files a task should change; a sandbox limits where commands run. Neither says whether this agent may run *this* command against *this* resource. A `db:reset` script is harmless against a scratch database and destructive against a shared one, and its name does not tell you which.

## Mechanism

Deny by default and write the policy down in six sections: **Read, Write, Commands, Secrets, Requires approval, Grants**. Judge the target resource and the consequence, not whether a command sounds dangerous. When the agent is blocked, it reports a typed refusal with the exact action and the grant that would allow it:

```text
COMMAND_NOT_ALLOWED: pip install freezegun==1.5.1
Needed for: freezing the clock in test_age_correct_behind_and_ahead_of_utc
Grant requested: one install into the local venv, this session only
```

Codes: `SECRET_PATH_DENIED`, `PATH_OUTSIDE_SURFACE`, `PROTECTED_FILE_DENIED`, `COMMAND_NOT_ALLOWED`, `DESTRUCTIVE_ACTION_REQUIRES_APPROVAL`. The agent never grants itself anything; grants are recorded with their scope and expiry.

## Worked example

`docs/authority.md` is the annotated policy for the Jyotish Coach lab: reads deny `.env`, keys and `secrets/**` even inside allowed folders; writes are the feature's expected surface plus the checkpoint; the ledger, evidence, policy files and verification config are protected; commands are exact strings (`python3 *` would allow anything); and schema changes, destructive store operations, dependency installs and publishing need a named human approval.

## Enforcement is separate from policy

An instruction file is guidance. For each rule, record what actually enforces it:

| Rule | Real enforcement |
| --- | --- |
| Read denials | The agent tool's permission deny rules; keep secrets out of the workspace |
| Write scope | Tool permissions during the session; `harness_check.py --session` after it |
| Protected files | CODEOWNERS, branch protection, the transition log replay |
| Commands | Exact allow lists; sandboxed runners |
| Secrets | Inject only sandbox credentials |

## Try it

Copy the blank template at the end of `docs/authority.md`, fill it for one project, and fill the "Enforced by" section honestly. Every row that says "instruction file" is a rule a model can ignore.

## Limits

This kit enforces write scope after the fact and protects the ledger through log replay. It does not intercept commands or reads during a session: that is the agent tool's job. See [Sandbox Enforcement Matrix](Sandbox%20Enforcement%20Matrix.md) for how enforcement differs by route.

## Connected concepts

- [Secret Handling](Secret%20Handling.md)
- [Three Tools and One Permit](../09%20-%20Tools%20and%20Interfaces/Three%20Tools%20and%20One%20Permit.md)
- [Destructive Database Reset](../12%20-%20Case%20Studies/Destructive%20Database%20Reset.md)
- [Scope Contract](../05%20-%20Scope/Scope%20Contract.md)
