# Cold-Session Checkpoint

A checkpoint must allow a fresh session to continue without relying on the previous conversation.

Record:
1. Active feature and observable outcome.
2. Current revision and dirty changes.
3. Verified commands and results.
4. Current failures: expected versus observed.
5. Decisions or constraints that must be preserved.
6. Important diagnosis not obvious from the repository.
7. Exact first command for the next session.
8. Next bounded edit if the failure reproduces.
9. Grants used this session: id, action, resource, approver, reason (see `docs/authority.md`). Grants expire with the session.

Avoid vague statements such as "almost done." Record observable facts.
