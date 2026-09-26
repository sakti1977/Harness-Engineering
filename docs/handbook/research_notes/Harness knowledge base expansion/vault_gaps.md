# Vault coverage, evidence, and practical expansion audit

## What does the existing vault cover, and where does its evidence stop?

### Takeaway

The vault has a useful control-oriented skeleton, but its next improvement should be verifiable provenance and runnable examples rather than more short definitions. This is a local content audit plus targeted primary-source research, checked 2026-09-26; it is not a claim to have exhausted all trustworthy publications.

### Cited Findings

- Local audit baseline: **44 Markdown files: 43 notes plus README, 6,395 whitespace-delimited words, zero HTTP(S) URLs**. These counts exclude the new `research_notes` directory. All existing wikilink targets resolve by filename. Two substantive notes have no incoming wikilinks: `Copilot Project Instructions` and `Case Studies - MOC`. README also has no incoming wikilink, which is normal for an entry point. Evidence is the local vault snapshot: [README](../../README.md), [main index](../../00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md), [source index](../../00%20-%20Start%20Here/Source%20Coverage%20Index.md).
- The source index maps 24 section titles to notes, but provides no original author, date, publication, URL, version, or archived text. The main index explicitly says the notes synthesize earlier shared conversation material. Consequently this is thematic coverage, not an independently verifiable bibliography. [Source Coverage Index](../../00%20-%20Start%20Here/Source%20Coverage%20Index.md)
- The practical implementation note identifies `sakti1977/Harness-Engineering` as the user's GitHub reference repository. This clue is present even though no configured local Git remote is available. Its claims about that repository need separate repository verification. [Copilot Project Instructions](../../11%20-%20Practical%20Implementations/Copilot%20Project%20Instructions.md)
- The five-layer vocabulary Reach/Power/Ground/Verdict/Carry is the vault's organizing model. Its origin is not identified as an external standard. Preserve it as a local synthesis unless original attribution is recovered. [Five Layers of a Harness](../../01%20-%20Foundations/Five%20Layers%20of%20a%20Harness.md)
- Examples such as a 612-line root instruction file and deletion of 1,412 bookings have no incident source. Treat these as instructional scenarios, not verified production incidents. [AGENTS.md as a Map](../../02%20-%20Reach/AGENTS.md%20as%20a%20Map.md), [Destructive Database Reset](../../12%20-%20Case%20Studies/Destructive%20Database%20Reset.md)

### Inferences

Coverage assessment below is my judgment from reading all 44 files, not a benchmark score.

| Area | Existing coverage | Missing depth or artifact |
|---|---|---|
| Foundations and navigation | Five layers, glossary, linear learning path, MOCs | Harness vs model vs evaluation harness; source confidence; audience-specific entry routes |
| Reach | Discovery funnel, authoritative repo context, root instructions, cold audit | Knowledge freshness, claim provenance, conflicting instructions, retrieval quality experiments |
| Power | Permit boundary, authority policy, secret protection, path checks | Prompt injection, network egress, authenticated connectors, identity and trust boundaries |
| Ground | Initialization, readiness, seeded environment, fidelity | Pinned dependencies, isolation between trials, CPU/RAM/time limits, environment manifests |
| Scope | Outcome, exclusions, amendment and discovery rules | Concrete filled template and counterexamples; explicit budget completion rules |
| Verdict | Claim-to-proof, ledger state, real-boundary evidence | Repeated stochastic trials, grader calibration, benchmark limitations, contamination |
| Carry | Journal, checkpoint, compaction, resume/replay/fork | Idempotent external writes, crash reconciliation, retention/version migration |
| Runtime | Provider seam and bounded loop | Retry policy, transient error classification, backpressure, explicit termination taxonomy |
| Tools | Permit, contracts, safe anchors, UI cancellation | MCP security, tool schema conformance, external side-effect reconciliation |
| Testing | Deterministic control fixtures, mutation testing, artifact receipts | Implemented fixtures and commands; capability vs regression suites; performance experiments |
| Observability | Event IDs and first divergence | Standard trace mapping, measured latency/cost, privacy-aware content capture |
| Multi-agent work | Indirect references in planner/worker/verifier and fork | Delegation criteria, bounded assignments, shared-state ownership, aggregation and cost |
| Learning usability | Uniform headings and reflection prompts | Worked examples, lab acceptance criteria, note-specific questions, evidence maturity labels |

### Gaps

- Earlier shared source material is unavailable in this audit; its authorship, dates, and original wording cannot be reconstructed reliably.
- No original real-world incident evidence was supplied for the clinic cases.
- No learning outcome assessment exists, so this audit cannot claim the present notes improved learner performance.

## Which primary sources close the most important technical gaps?

### Takeaway

Add a small set of source-backed notes about evaluation, infrastructure, connector security, tracing, retries, and coordination. Keep general lessons distinct from product-specific implementation and internal vendor experiments.

### Cited Findings

- **Evaluation:** Anthropic distinguishes an agent harness from an evaluation harness, separates final environmental outcome from transcript, recommends repeated trials, and distinguishes capability from regression suites. Its guidance contrasts success in at least one of k attempts (`pass@k`) with consistency across all k (`pass^k`), and calls for human calibration of model graders. This is vendor engineering guidance, not a guarantee about every agent. [Demystifying evals for AI agents, 2026-01-09](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- **Environment:** Anthropic reports a six-percentage-point Terminal-Bench 2.0 difference between its least- and most-resourced internal configurations, and argues resource configuration should be an experimental variable. Do not generalize the numerical result to another benchmark or harness. [Quantifying infrastructure noise, 2026-02-05](https://www.anthropic.com/engineering/infrastructure-noise)
- **Connector security:** MCP's current security guidance covers confused-deputy problems, token audience validation, token passthrough, and SSRF; token passthrough is forbidden by its authorization specification. This expands the vault's local file and shell policy to remote identity and network boundaries. [MCP Security Best Practices, versioned documentation](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)
- **Observability:** The original OpenTelemetry GenAI documentation now redirects readers to a separate repository. Its agent/framework span specification includes agent invocation and tool execution and is marked Development. Pin a version when teaching attribute names. [Move notice](https://opentelemetry.io/docs/specs/semconv/gen-ai/), [official agent spans specification](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)
- **Reliable effects:** AWS explains how an operation can succeed while its response is lost, making blind retry unsafe, and describes client request identifiers for idempotent behavior. Its treatment includes repeated identifiers with different intent and late-arriving requests. [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- **Retry timing:** AWS documents exponential backoff with jitter and notes support in its SDK retry modes. This is a reusable distributed-systems pattern, not an agent-specific guarantee. [Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- **Coordination:** Anthropic reports that its research system used an orchestrator and parallel subagents, while tasks with strongly shared context or dependencies were less suitable. It also reports substantial token overhead; its observations concern its research workload and models. [How we built our multi-agent research system, 2025-06-13](https://www.anthropic.com/engineering/multi-agent-research-system)

### Inferences

These are **proposed knowledge-base additions**, not claims that the sources prescribe these exact files or designs. P0 means establish first; P1 means next practical expansion; P2 means deepen after the basics work.

| # | Priority | Proposed note or edit | Concrete content and demonstration |
|---|---|---|---|
| 1 | P0 | `00 - Start Here/Source Register.md` | Link every externally factual claim to publisher/date/URL/version; separate source findings, local choices, and hypotheses. Flag unrecovered legacy provenance. |
| 2 | P0 | `01 - Foundations/Agent Harness and Evaluation Harness.md` | Draw the boundary between model, tool runtime, task environment, grader, and suite; show which component caused a sample failure. |
| 3 | P0 | `03 - Power/Untrusted Content and Prompt Injection.md` | Threat-model README, retrieved pages, tool results, and malicious test output; show an attempted instruction crossing a trust boundary and the expected denial. Obtain dedicated primary security evidence before presenting as a complete mitigation recipe. |
| 4 | P0 | `03 - Power/MCP Identity and Network Boundaries.md` | Diagram client/server/downstream API identities; invalid-audience token, confused deputy, private-network request fixtures. Keep local process permissions and remote authorization distinct. |
| 5 | P0 | `10 - Harness Testing/Agent Evaluation Suite.md` | Small representative task bank with initial state, success criteria, outcome grader, transcript link, repeated-trial settings, and capability/regression classification. |
| 6 | P0 | `11 - Practical Implementations/First Executable Harness Lab.md` | Convert the existing false-green booking scenario into a runnable red/green fixture with exact setup, proof command, expected evidence, cleanup, and a deliberately broken control. |
| 7 | P1 | `10 - Harness Testing/Grader Reliability.md` | Demonstrate false reject, false accept, ambiguous task, valid alternate solution, protected grader, and human-calibrated rubric; separate task failure from grader failure. |
| 8 | P1 | `04 - Ground/Reproducible Evaluation Environment.md` | Record image/dependency versions, seed, model config, CPU/RAM, timeout, concurrency and network assumptions. Show a resource failure classified separately from a behavioral failure. |
| 9 | P1 | `08 - Agent Runtime/Retry and Idempotency Contract.md` | Classify transient vs permanent failures; bounded attempts and jitter; external write key; crash-after-effect-before-receipt reconciliation; same key/different intent rejection. |
| 10 | P1 | `06 - Verdict/Traces Metrics and Privacy.md` | Map existing run/turn/tool IDs into trace/span relationships. Collect cost, tokens, latency, denial, timeout and retries. Redact content; pin the evolving semantic-convention version. |
| 11 | P1 | `08 - Agent Runtime/Delegation and Shared State.md` | Compare one agent with independent subtask delegation on the same task/budget. Require task ownership, output contract, source evidence, timeout, cancellation and integration responsibility. |
| 12 | P1 | `10 - Harness Testing/Harness Ablation Experiments.md` | Compare baseline with one changed control while holding task/environment/model settings fixed. Report success, cost and time; make overhead and regressions visible. |
| 13 | P1 | Extend `07 - Carry/Context Compaction Contract.md` | Filled before/after checkpoint example with preserved authority, unresolved effects and evidence references. Add a cold-resume exercise and a test for invented summary facts. |
| 14 | P2 | `12 - Case Studies/Case Evidence and Reproduction Template.md` | Mark observed incident vs hypothetical scenario; include source, version, initial state, minimal reproduction, impact, causal uncertainty and control effectiveness. Replace unsupported numeric precision where no original source exists. |
| 15 | P2 | Extend `00 - Start Here/Learning Path.md` | Add reader and builder routes; link each milestone to one artifact and observable completion check. Replace identical reflection prompts with questions about the note's specific tradeoffs. |

### Gaps

- The suggested prompt-injection note needs its own focused primary-source review; MCP authorization guidance is not sufficient evidence for all prompt-injection defenses.
- No lab was executed as part of this research assignment. All proposed labs and metrics are implementation work, not completed results.
- No universal optimal delegation count, retry count, review interval, or context budget can be inferred from these sources.

## How should this research be integrated without overwhelming the vault?

### Takeaway

Use one research entry note, one prioritized backlog, and two lightweight templates. Keep the existing conceptual organization, but make source status and practical completion visible.

### Cited Findings

- The main MOC currently routes to five layer MOCs and the learning path; it does not directly route to the case-study MOC or Copilot implementation note. The source index is organized around the earlier 24-part text. [Main MOC](../../00%20-%20Start%20Here/Harness%20Engineering%20-%20MOC.md), [Source Coverage Index](../../00%20-%20Start%20Here/Source%20Coverage%20Index.md)

### Inferences

Suggested compact integration:

1. Add `[Harness Improvement Roadmap](../../00%20-%20Start%20Here/Harness%20Improvement%20Roadmap.md)` under an explicit Research and improvement heading in the main MOC and Source Coverage Index. In the source index, preserve the 24-section legacy mapping and explain that it records thematic correspondence, while the new source register supplies external provenance.
2. Put the collected findings in `13 - Research/Harness Knowledge Base Expansion.md`, with links to the report, source register, and `Enhancement Backlog.md`. Keep researcher working files in `research_notes` as supporting material.
3. Link `[Case Studies - MOC](../../12%20-%20Case%20Studies/Case%20Studies%20-%20MOC.md)` and `[Copilot Project Instructions](../../11%20-%20Practical%20Implementations/Copilot%20Project%20Instructions.md)` from the main MOC or learning path to fix the two meaningful discoverability gaps.
4. Use the backlog above with fields `priority`, `existing-note`, `new-note`, `source`, `artifact`, `acceptance-check`, `status`. Set new items to `proposed`, not implemented or verified.
5. Add templates under `Templates/` only when used; avoid creating empty notes for every suggested topic.

Reusable concept-note template proposal:

```markdown
---
type: concept
status: proposed
evidence_kind: synthesis
reviewed: YYYY-MM-DD
source_ids: []
related: []
---
# Concept title
## Problem and when it matters
## Mechanism and boundary
## Worked example
## Evidence
Source-supported claim — [primary source](URL), section/version.
## Local recommendation
State the proposed design and assumptions explicitly.
## Verification
Fixture, action, expected observation, failure case.
## Tradeoffs and limits
## Connected concepts
```

Reusable source-note template proposal:

```markdown
---
type: source
publisher:
author:
published:
accessed: YYYY-MM-DD
url:
version_or_commit:
source_kind: official-docs
confidence: primary-source
---
# Source title
## Scope
What the source can and cannot establish.
## Supported claims
Concise paraphrase with section or stable link.
## Local implications
Clearly marked proposals linked to concept notes.
## Caveats
Vendor report, internal experiment, draft standard, or unreplicated result.
## Review triggers
New release, changed specification, broken link, or conflicting evidence.
```

### Gaps

- These integration changes and templates are recommendations only; this audit writes only its assigned research file.
- Existing notes have no granular source-to-claim mapping. Retrofitting citations should not imply that new sources authored the vault's original terminology or examples.
