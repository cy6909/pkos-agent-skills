# Developer self-test and shared independent testing

## Mandatory developer evidence

Before T-SHARED-01 receives a candidate, the developer must provide the exact pushed SHA, a clean `remote-12` checkout, directed test result, typecheck/build result, and acceptance mapping. Web work additionally requires public-production self-test in real Chrome under identity `cy6909`. Local tests, local services, Docker, private origin, and claims without evidence do not qualify.

The developer owns product code and its self-test. The shared tester independently verifies; it never substitutes for self-test, repairs product code, changes requirements, or merges candidates. A failed self-test returns directly to the same affinity-matched developer.

## Progressive MFSQ

1. Layer 1: P0 user smoke and critical writes.
2. Layer 2: exceptions, idempotency, permissions, and recovery.
3. Layer 3: performance, long-run stability, and cross-device/platform.

Do not expand layer 3 while layer 1 fails. Do not pre-author large low-priority suites before a candidate exists. T-SHARED-01 tests the latest integrated candidate SHA and returns a <=600-character settlement with evidence links and P0/P1 defects.

## Continuous integration handoff

After developer self-test, TD-01 integrates immediately into the same cumulative candidate and sends only the candidate delta to T-SHARED-01. Completion order determines opportunity, not a wait-all barrier. A new lane result never creates a parallel candidate.
