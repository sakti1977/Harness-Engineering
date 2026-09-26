---
type: concept
status: maintained
evidence_kind: source-backed-synthesis
reviewed: 2026-09-26
tags: [harness-engineering]
---

# Knowledge Base Maintenance

## Problem

A note can be readable, discoverable and wrong. Stale commands and undocumented assumptions consume future sessions.

## Mechanism

Give maintained notes an evidence kind, review date, owner role and links to supporting sources. Keep an authoritative location for each rule. Route from an index instead of duplicating whole policies. Use mechanical checks for links and source identifiers, then human review for whether the source actually supports the claim.

## Worked example

A runtime upgrade changes cancellation behavior. Mark the affected note for review, pin the old behavior to its version, and rerun its fixture before changing the recommendation. A working URL alone is insufficient.

## Try it and check the result

Copy [[Source Note Template]] for one source used by your project. Name the supported claim and a review trigger. Run the repository’s documentation checker after changing a link. Separately inspect the cited section for semantic accuracy.

## Tradeoffs and limits

A review date is evidence of inspection, not a promise of freshness. Start with the highest-impact notes. Maintain one canonical Markdown body and generate alternate GitHub navigation; avoid hand-editing both exports.

## Sources and interpretation

[OpenAI: harness engineering](https://openai.com/index/harness-engineering/) describes documentation maintenance and mechanical checks. The metadata and review workflow here are local recommendations.

The worked example and exercise are local teaching designs unless identified as executed in [[Vault Update Record]]. Source findings do not establish that this design is best for every project.

## Connected concepts

- [[Source Register]]
- [[Source Coverage Index]]
- [[Repository as Shared Context]]
