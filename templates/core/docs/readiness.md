# Readiness Contract

Initialization is a gate, not a repair bot.

Before feature work begins verify:
- runtime/version is supported
- configuration is usable without exposing secrets
- required seed/test data exists
- the real service boundary is reachable
- the baseline verification command can judge the system

Report probes as `PASS`, `FAIL`, or `SKIP`.

`READY` means every required probe passes. If a prerequisite fails, dependent checks may be skipped and feature work remains blocked.
