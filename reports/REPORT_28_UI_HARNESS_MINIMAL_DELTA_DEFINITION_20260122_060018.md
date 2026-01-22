---
doc_id: report_ui_harness_minimal_delta_definition_20260122_060018
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
tags: [report, ui, harness, mvp, context]
---

# REPORT 28 — UI HARNESS MINIMAL DELTA DEFINITION

## Non-Goals (Explicit)
- No interpretation or optimization.
- No status/health colors or summaries.
- No KPIs, rankings, or scoring.
- No recommendations or prescriptive guidance.
- No dashboards or aggregation on ledger surfaces.
- No new workflows beyond manual MVP exercising.

---

## Required Harness Surfaces (Exact)

### A) Mode Selector
**Purpose:** Explicit mode selection and auditable client state.  
**UI:** Radio toggle; current mode displayed.  
**Behavior:** Sets `X-Ops-Mode` header on all requests.

**Endpoints:** none (client-side only)

**Fields displayed:**
- current mode (execution | planning)

---

### B) Ops Action Exerciser (Execution)
**Purpose:** Emit a real Ops exhaust event with minimal required fields.  
**Endpoint:** `POST /ops/carrier_handoff`  
**Required fields:**
- `subject_ref` (string)
**Optional fields:**
- `carrier` (string)
- `event_data` (object)

**Fields displayed (response):**
- `success`
- `event_id`
- error payload if refused/invalid

---

### C) Cutter Ledger Viewer (Planning)
**Purpose:** Chronological, raw events (no aggregation).  
**Endpoint:** `GET /api/cutter/events`  
**Optional filters:**
- `subject_ref`
- `event_type`
- `limit`

**Fields displayed (response):**
- `events` (raw event list)

---

### D) State Ledger Viewer + Entry (Planning)
**Purpose:** Explicit declarations + chronological history.  

**Entry endpoint:** `POST /api/state/declarations`  
**Required fields:**
- `entity_ref`
- `scope_ref`
- `actor_ref`
- `declaration_kind` (REAFFIRMATION | RECLASSIFICATION)
- `state_text`
**Optional fields:**
- `cutter_evidence_ref`
- `evidence_refs` (array)
- `supersedes_declaration_id`

**Viewer endpoint:** `GET /api/state/declarations`  
**Optional filters:**
- `entity_ref`
- `scope_ref`
- `actor_ref`
- `limit`

**Fields displayed (responses):**
- `declaration_id` (POST)
- `declarations` (GET, chronological list)

---

### E) Reconciliation Surface (MVP-12, Planning)
**Purpose:** Explicit, query-scoped reconciliation (non-blocking).  

**Record endpoint:** `POST /api/reconcile`  
**Required fields:**
- `scope_ref`
- `scope_kind` (query | report)
- `predicate_ref`
- `actor_ref`
**Optional fields:**
- `predicate_text`

**Viewer endpoint:** `GET /api/reconcile`  
**Optional filters:**
- `scope_ref`
- `scope_kind`
- `predicate_ref`
- `actor_ref`
- `limit`

**Fields displayed (responses):**
- `reconciliation` (POST)
- `reconciliations` (GET, chronological list)

---

### F) Refusal Tester (MVP-15, Planning)
**Purpose:** Trigger explicit refusal and verify refusal event.  

**Refusal endpoint:** `POST /api/query/refusal`  
**Required fields:**
- `query_ref`
- `actor_ref`
**Optional fields:**
- `query_text`

**Refusal event viewer:** `GET /api/cutter/events` with `subject_ref=query:{query_ref}`

**Fields displayed (responses):**
- `refusal` payload (category, reason, query_ref, query_class)
- `event_id`
- refusal event in Cutter Ledger list

---

## Hard Gate
No harness implementation changes are permitted until this report exists.
