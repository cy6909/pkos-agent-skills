# Single-candidate delivery lifecycle

```text
G0 freeze Features/scopes -> G1 executable readiness
-> developer self-test -> immediate TD-01 cumulative integration
-> shared independent P0-first testing -> repeat on same candidate
-> G3 freeze -> conditional G4 strict review -> G5 deployment/real acceptance
```

TD-01 maintains exactly one candidate per generation. Each eligible lane SHA is integrated immediately; the candidate SHA is updated in place and prior SHA remains evidence, not a live parallel candidate. Shared ownership is settled before dispatch.

G3 freezes only after required Features, self-tests, independent tests, deployment path, traceability, and P0/P1 state agree. RB-01 may start only after freeze and only for high-risk security/ledger/migration/permission work, explicit strict acceptance, or obvious abnormal behavior. Ordinary clear work has no early Reviewer.

`ACCEPT | RETURN_TO_LANE | BLOCKED_EXTERNAL_BOUNDARY` are valid strict outcomes. Two consecutive returns stop new Features and enter root-cause consolidation. Repair uses the same affinity task and a new generation, then updates/refreezes the same logical candidate.

G5 accepts the exact frozen candidate after remote-12 evidence and, for Web, public-production real `cy6909` Chrome acceptance. Governance completeness cannot substitute for a deployable, real-accepted product.
