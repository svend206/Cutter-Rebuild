---
doc_id: report_ui_harness_verification_evidence_20260122_060332
doc_type: context
status: active
version: 1.0
date: 2026-01-22
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/BOOT_CONTRACT.md]
conflicts_with: []
tags: [report, ui, harness, verification, mvp, context]
---

# REPORT 29 — UI HARNESS VERIFICATION EVIDENCE

## Surface Evidence (HTML Snippets)

```
<div class="banner">
  <h1>HARNESS v0 — NOT PRODUCT UX</h1>
  <div class="note">Manual MVP exerciser. No dashboards, no scoring, no interpretation.</div>
</div>
<div class="panel">
  <h2>Mode Selector</h2>
  <label><input type="radio" name="ops-mode" value="execution" checked /> Execution</label>
  <label><input type="radio" name="ops-mode" value="planning" /> Planning</label>
  <div class="note">Current mode: <span id="mode-current">execution</span></div>
</div>
```

```
<div class="panel" data-mode="execution">
  <h2>Ops Action Exerciser (Execution)</h2>
  <form id="ops-action-form">...</form>
</div>
<div class="panel" data-mode="planning">
  <h2>Cutter Ledger Viewer (Planning)</h2>
  <form id="cutter-events-form">...</form>
</div>
```

## Endpoints Called (Per Surface)
- Mode selector: client-only; sets `X-Ops-Mode` header on all requests.
- Ops action exerciser: `POST /ops/carrier_handoff`
- Cutter Ledger viewer: `GET /api/cutter/events`
- State Ledger entry: `POST /api/state/declarations`
- State Ledger viewer: `GET /api/state/declarations`
- Reconciliation record: `POST /api/reconcile`
- Reconciliation viewer: `GET /api/reconcile`
- Refusal tester: `POST /api/query/refusal`
- Refusal event viewer: `GET /api/cutter/events?subject_ref=query:{query_ref}`

## Manual Happy Path Script
1. Open `/harness` and confirm banner “HARNESS v0 — NOT PRODUCT UX”.
2. Select **Execution** mode.
3. Submit Ops action:
   - `subject_ref = quote:demo-1`
   - optional `event_data = {"note":"manual test"}`
   - Expect success with `event_id`.
4. Switch to **Planning** mode.
5. Load Cutter events:
   - `subject_ref = quote:demo-1`
   - Expect event list with the emitted record (chronological order).
6. Submit State declaration:
   - `entity_ref = org:demo.com/entity:project:alpha`
   - `scope_ref = org:demo.com/scope:weekly`
   - `actor_ref = org:demo.com/actor:owner`
   - `declaration_kind = REAFFIRMATION`
   - `state_text = "Operations continue."`
7. Load State declarations and confirm the new entry appears.
8. Record reconciliation:
   - `scope_ref = org:demo.com/scope:weekly`
   - `scope_kind = query`
   - `predicate_ref = predicate:open_deadlines`
   - optional `predicate_text = "actual_time > promised_time"`
9. Load reconciliations and confirm the record is listed.
10. Submit refusal query:
    - `query_ref = query:blame:example`
    - `actor_ref = org:demo.com/actor:owner`
    - Expect explicit refusal payload.
11. Load refusal events and confirm `REFUSAL_EMITTED` appears in Cutter Ledger list.

## No Aggregation / Interpretation Statement
All harness surfaces render raw JSON payloads only and enforce mode-specific access. There are no dashboards, scoring, rankings, or interpretive labels, and ledger views remain chronological and unaggregated.
