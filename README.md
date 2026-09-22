# Harness Engineering

A practical reference repository for building reliable AI coding-agent environments.

> **Capability is what the model can do. Reliability is what the system lets it finish.**

## The five-layer model

| Layer | Question | Main artifact |
|---|---|---|
| **Reach** | Can the agent find what matters? | Copilot instructions + focused docs |
| **Power** | What may it read, write, and execute? | Authority Policy |
| **Ground** | Is the environment real and ready? | Readiness Contract |
| **Verdict** | What evidence proves the behavior? | Claim-to-Proof Matrix |
| **Carry** | What survives when the session ends? | Cold-session checkpoint |

## Repository structure

```text
.github/
  copilot-instructions.md

docs/
  authority.md
  scope-contract.md
  proof-matrix.md
  readiness.md

.harness/
  checkpoint.md
  feature.json

scripts/
  harness_check.py
```

## Run the sample harness check

```bash
python scripts/harness_check.py
```

The checker validates the presence and basic shape of the harness-control artifacts. It deliberately does **not** call an AI model: harness controls should be testable deterministically.

## How to use this in a real project

Start by copying `.github/copilot-instructions.md`. Then customize the project-specific documentation and harness artifacts rather than turning the root instruction file into an encyclopedia.

A useful adoption order is:

1. Recovery Audit
2. Readiness gate
3. Scope Contract
4. Authority Policy
5. Claim-to-Proof Matrix
6. Cold-session checkpoint
7. Harness-control tests
8. Safe edit contract
9. Durable journal/resume
10. Release evidence

Grow the harness from observed failures. When an agent makes a repeatable mistake, ask which harness control should make that class of mistake harder, visible, or impossible next time.

## Design principle

Prompt engineering tells the model what you want.

**Harness Engineering determines what happens when the model acts.**
