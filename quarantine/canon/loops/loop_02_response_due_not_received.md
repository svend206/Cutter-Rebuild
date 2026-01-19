---
doc_id: quarantine_loop_02_response_due_not_received
doc_type: context
status: quarantined
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [quarantine]
---

Source: Cutter Layers/canon/loops/loop_02_response_due_not_received.md

---
doc_id: loop_02_response_due_not_received
doc_type: spec
status: active
version: 0.1
date: 2026-01-16
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: []
source: cursor
locks: [phases_1_2_3]
---

# Loop 2 — Response Due But Not Received

## Anchor
State Ledger uses:
entity_ref = "entity:<opaque-id>" (canonical identifier)
scope_ref = "promise:response_by"
state_text = {"deadline":"<ISO-8601>"}

Declared only via State Ledger.

State and Cutter share the same opaque identifier value to prevent meaning collapse via mapping layers.

## Minimal Ops Exhaust

Required event types (facts only):

- request_sent
  - subject: entity:<opaque-id> (must equal State entity_ref)
  - channel (opaque, optional)
  - counterparty (opaque, optional)
  - ts

- response_received
  - subject: entity:<opaque-id> (must equal State entity_ref)
  - ts

No derived states. No labels. No aggregation.

## Expected Durations

Expected response durations live in Ops config only.
They are not promises and do not appear in any ledger.

## Canonical Queries

### Query A — Promises Not Closed by Reality
promise:response_by declarations with no response_received event, anti-joined directly on the shared identifier value (entity_ref == subject_ref), with no translation.

Raw output only:
- entity_ref
- response_by
- declared_at
- declared_by_actor_ref

### Query B — Time Since Request vs Expectation
Elapsed time since request_sent vs expected duration.

Raw output only:
- entity_ref
- elapsed_time
- expected_time
- delta

## Natural Language Routing Rule (Surface Match Only)

Examples:
- "Waiting on a response"
- "Response due but not received"
- "No response yet"
- "Response deadline"

No inference.
No synthesis.
No new concepts.
