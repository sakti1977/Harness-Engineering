---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Sandbox Enforcement Matrix

## Problem

A policy can deny one editor tool while the same write remains possible through a shell or connector.

## Mechanism

Inventory enabled routes: read, edit, shell, subprocess, network and remote services. For each protected resource record the intended rule, enforcing component, supported platform and observed test result. Distinguish guidance, configuration and exercised enforcement. A local directory check is not OS containment.

## Worked example

An editor hook rejects a protected file. A shell can still modify it unless the shell boundary applies the same policy. A test must inspect the file after both attempts, rather than merely looking for a denial message.

## Try it and check the result

Design clean and forbidden requests for each route in an isolated environment. Record OS, runtime version, child-process behavior and before/after hashes. If the boundary cannot be exercised on the current host, label it untested rather than passed.

## Tradeoffs and limits

Deny-by-default policies can block legitimate workflows. Maintain a narrow, reviewable exception path. Do not run adversarial writes on production resources. This vault does not ship or certify a sandbox.

## Sources and interpretation

[Codex: core implementation notes](https://github.com/openai/codex/blob/main/codex-rs/core/README.md) describes platform-specific enforcement. [smolagents](https://github.com/huggingface/smolagents) explicitly distinguishes its local executor from a security sandbox.

The worked example and exercise are local teaching designs unless identified as executed in [Vault Update Record](../00%20-%20Start%20Here/Vault%20Update%20Record.md). Source findings do not establish that this design is best for every project.

## Connected concepts

- [Authority Policy](Authority%20Policy.md)
- [Harness-Control Tests](../10%20-%20Harness%20Testing/Harness-Control%20Tests.md)
- [Untrusted Content and Prompt Injection](Untrusted%20Content%20and%20Prompt%20Injection.md)
