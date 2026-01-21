---
doc_id: mvp_gap_analysis
doc_type: archive
status: archived
version: 1.6
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [reports/REPORT_1_CURRENT_CAPABILITY_INVENTORY.md, reports/REPORT_2_SYSTEM_SURFACES_AND_ENTRYPOINTS.md, reports/REPORT_3_DATA_AND_SCHEMA_FACTS.md, reports/REPORT_4_TEST_AND_RUNTIME_STATUS.md, reports/REPORT_5_GOVERNANCE_INTEGRITY_CHECK.md]
conflicts_with: []
tags: [mvp, gap, planning, context, archive]
---

# MVP Gap Analysis — Current State vs Locked MVP

Archived from `architecture/MVP Gap Analysis.md` on 2026-01-19.

**Status:** Active

This document compares the **locked MVP capability definition** against the system’s **current, evidenced capabilities**, using *only* the five factual reports provided by Cursor:

* REPORT 1 — Current Capability Inventory
* REPORT 2 — System Surfaces & Entrypoints
* REPORT 3 — Data & Schema Facts
* REPORT 4 — Test & Runtime Status
* REPORT 5 — Governance Integrity Check

No inference, planning, sequencing, or solution proposals appear in this document.

---

## MVP-1 — Ops can perform work and emit exhaust

**Status:** Implemented

**Evidence:**
Ops supports quoting, outcomes, status updates, customer/contact management, and related actions, all of which emit operational exhaust. Append-only enforcement exists for exhaust tables.
(Reports 1, 3, 4)

---

## MVP-2 — Cutter Ledger preserves demonstrated operational reality

**Status:** Implemented

**Evidence:**
`cutter__*` tables are append-only with trigger enforcement and WAL mode enabled. Ledger queries and tests demonstrate preservation of sequence and duration without overwrite.
(Reports 3, 4)

---

## MVP-3 — Cutter Ledger is read-only with respect to meaning

**Status:** Implemented

**Evidence:**
No schema fields, APIs, or tests encode success/failure, health, priority, or recommendations within Cutter Ledger data or queries.
(Reports 1, 3, 4)

---

## MVP-4 — State Ledger supports explicit human recognition

**Status:** Implemented

**Evidence:**
State declarations are explicit, append-only, and tied to recognition owners. Tests verify declaration behavior and schema constraints.
(Reports 3, 4)

---

## MVP-5 — State continuity requires explicit reaffirmation

**Status:** Implemented

**Evidence:**
State declarations require explicit reaffirmation or reclassification, and time-in-state is visible via derived state views and test coverage.
(Reports 1, 3, 4)

---

## MVP-6 — Evidence may be referenced but never evaluated

**Status:** Implemented

**Evidence:**
State declarations support inert evidence references with test coverage and schema support.
(Reports 1, 3, 4)

---

## MVP-7 — Separation between Ops, Cutter Ledger, and State Ledger is enforced

**Status:** Implemented

**Evidence:**
Ops emits exhaust without declaring state; ledgers do not trigger Ops behavior or inference. Governance checks report no boundary violations.
(Reports 1, 5)

---

## MVP-8 — Explicit, downstream-only Guild exhaust export

**Status:** Implemented

**Evidence:**
Exports require explicit actor_ref initiation and provide raw additive records with provenance metadata.
(Reports 1, 2, 4)

---

## MVP-9 — System authority is document-governed and non-inventive

**Status:** Implemented

**Evidence:**
Single boot contract, single status surface, single app entrypoint, and no duplicate constitutional authority detected.
(Report 5)

---

## MVP-10 — Absence of action is a preserved, inspectable fact

**Status:** Implemented

**Evidence:**
Unclosed quotes expose elapsed time without outcomes, and state time-in-state exposes elapsed time since last declaration without inference.
(Reports 1, 3, 4)

---

## MVP-11 — Ops enforces separation of execution and planning modes

**Status:** Implemented

**Evidence:**
Ops enforces explicit ops_mode separation and strips planning-only signals during execution; test coverage exists for execution guard behavior.
(Reports 1, 4)

---

## Summary Table

| MVP Capability                           | Status                |
| ---------------------------------------- | --------------------- |
| MVP-1 Ops emits exhaust                  | Implemented           |
| MVP-2 Cutter Ledger preserves reality    | Implemented           |
| MVP-3 Cutter Ledger meaning-free         | Implemented           |
| MVP-4 Explicit state recognition         | Implemented           |
| MVP-5 Explicit reaffirmation required    | Implemented           |
| MVP-6 Evidence references inert          | Implemented           |
| MVP-7 Layer separation enforced          | Implemented           |
| MVP-8 Guild exhaust export               | Implemented           |
| MVP-9 Document-governed authority        | Implemented           |
| MVP-10 Absence of action preserved       | Implemented           |
| MVP-11 Ops execution/planning separation | Implemented           |

---

## Notes

* All judgments are based strictly on documented evidence or absence thereof in the five reports.
* “Partially Implemented” indicates structural presence without full, explicit MVP-level guarantees.
* This document intentionally contains **no remediation guidance, sequencing, or prioritization**.
