---
doc_id: quarantine_loop_01_late_shipment_turned_green
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

Source: Cutter Layers/canon/loops/loop_01_late_shipment_turned_green.md

---
doc_id: loop_01_late_shipment_turned_green
doc_type: spec
status: active
version: 0.1
date: 2026-01-16
owner: Erik
authoring_agent: chatgpt
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: []
source: chatgpt
locks: [phases_1_2_3]
---

# Loop 1 — Late Shipment that Turned Green

## Anchor
State Ledger uses:
entity_ref = "entity:<opaque-id>" (canonical identifier)
scope_ref = "promise:deadline"
state_text = {"deadline":"<ISO-8601>"}

Declared only via State Ledger.

For Loop 1, State and Cutter share the same opaque identifier value to prevent meaning collapse via mapping layers.

## Minimal Ops Exhaust

Required event types (facts only):

- stage_started
  - subject: entity:<opaque-id> (must equal State entity_ref)
  - stage: machining | inspection | packing
  - ts

- stage_completed
  - subject: entity:<opaque-id> (must equal State entity_ref)
  - stage: machining | inspection | packing
  - ts

- carrier_handoff
  - subject: entity:<opaque-id> (must equal State entity_ref)
  - ts
  - carrier (opaque, optional)

No derived states. No labels. No aggregation.

## Expected Durations

Expected stage durations live in Ops config only.
They are not promises and do not appear in any ledger.

## Canonical Queries

### Query A — Promises Not Closed by Reality
promise:deadline declarations with no carrier_handoff event, anti-joined directly on the shared identifier value (entity_ref == subject_ref), with no translation.

Raw output only:
- entity_id
- deadline
- declaration_ts
- declaring_actor

### Query B — Dwell-Time vs Expectation
Elapsed stage time vs expected duration.

Raw output only:
- entity_id
- stage
- elapsed_time
- expected_time
- delta

## Natural Language Routing Rule

Natural language may select one predefined query by surface match only.

No inference.
No synthesis.
No new concepts.
