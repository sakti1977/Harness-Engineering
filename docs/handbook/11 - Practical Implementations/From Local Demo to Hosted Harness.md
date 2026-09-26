---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
---

# From Local Demo to Hosted Harness

## The boundary changes

A local teaching example has one user, disposable data and a narrow execution path. Hosting introduces identity, tenant separation, durable storage, secrets, quotas, cleanup and operational recovery. A successful local example cannot establish these properties.

## Deployment design exercise

Draw the caller, application server, agent runtime, workspace and external tool services. For each connection, identify the authenticated principal, permitted resources, timeout and durable record. Keep model-generated claims separate from server-side authorization.

Specify tests for two tenants attempting to read each other’s state, a runtime restart during an in-flight action, expired credentials, cancelled jobs whose effects may already exist, and abandoned workspace cleanup. Use synthetic data and an isolated deployment environment. Record what the test actually exercises: a mock identity check differs from a deployed authentication boundary.

## Sources and limits

[OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) separates execution/workspace concerns from application ownership. [Anthropic’s chat demo](https://github.com/anthropics/claude-agent-sdk-demos/blob/main/simple-chatapp/README.md) identifies authentication, storage and isolation as production work beyond a local demo. Pin implementation versions before adapting code.

This note is a design checklist, not a hosted deployment recipe or a security certification. No hosted environment is supplied by this release. Start with [MCP Identity and Network Boundaries](../03%20-%20Power/MCP%20Identity%20and%20Network%20Boundaries.md), [Retry and Idempotency Contract](../08%20-%20Agent%20Runtime/Retry%20and%20Idempotency%20Contract.md), [Memory Scope and Retention](../07%20-%20Carry/Memory%20Scope%20and%20Retention.md) and [Traces Metrics and Privacy](../06%20-%20Verdict/Traces%20Metrics%20and%20Privacy.md).
