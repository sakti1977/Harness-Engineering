# Claim-to-Proof Matrix

Write acceptance claims before declaring completion.

| Claim | Observation required | Evidence producer |
|---|---|---|
| Invalid input is rejected | External response | API test |
| Rejected request changes no persistent state | Before/after state | DB assertion |
| Valid input succeeds | Response + persistent state | E2E test |

A claim is covered only when verification observes the behavior at the boundary that matters.

Unit tests can support a claim without proving the production path. For concurrency, persistence, integration, and external behavior, use the real boundary and shared state required by the claim.
