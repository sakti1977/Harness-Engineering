---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# MCP Identity and Network Boundaries

## Problem

A permitted tool call can still use the wrong identity, reach an unintended service or forward credentials to the wrong audience.

## Mechanism

Track the user, client, MCP server and downstream API separately. Validate token audience and scopes for the service receiving the token. Constrain destinations, redirects and address resolution at the network boundary. Treat local process access and remote authorization as distinct controls.

## Worked example

A server receives a token meant for a different API. Reject it at the receiving service rather than forwarding it downstream. A valid JSON tool request does not establish authorization.

## Try it and check the result

With synthetic credentials and a local mock service, specify cases for wrong audience, missing scope, an unexpected redirect and a disallowed destination. Check that denied cases produce no downstream call. Keep the fixture offline until an approved integration environment exists.

## Tradeoffs and limits

MCP security guidance is versioned and must be rechecked when the specification changes. It does not by itself solve prompt injection or tenant isolation. Credential values should never appear in traces.

## Sources and interpretation

[MCP: security best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) covers token audience, token passthrough, confused-deputy and SSRF risks. The proposed fixture is not an implemented MCP conformance suite.

The worked example and exercise are local teaching designs unless identified as executed in [[Vault Update Record]]. Source findings do not establish that this design is best for every project.

## Connected concepts

- [[Untrusted Content and Prompt Injection]]
- [[Secret Handling]]
- [[Typed Outputs and Semantic Validation]]
