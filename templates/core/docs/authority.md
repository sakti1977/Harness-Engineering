# Authority Policy

Default: deny.

The agent may read project source and documentation. It may write only inside the declared work surface and run approved verification commands.

The agent must not:
- read secret files such as `.env`
- print environment variables
- modify policy files to widen its own authority
- reset or destroy shared data without explicit approval
- publish or send external messages without approval
- rewrite Git history

## Stable refusal codes
- `SECRET_PATH_DENIED`
- `PATH_OUTSIDE_SURFACE`
- `COMMAND_NOT_ALLOWED`
- `DESTRUCTIVE_ACTION_REQUIRES_APPROVAL`

Capability and permission are separate. The agent may request an action; the harness decides whether the session may perform it.
