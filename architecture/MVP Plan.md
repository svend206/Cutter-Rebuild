---
doc_id: mvp_plan
doc_type: context
status: active
version: 1.0
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [bootstrap/MVP Capability Definition.md, architecture/MVP Gap Analysis.md, reports/REPORT_1_CURRENT_CAPABILITY_INVENTORY.md, reports/REPORT_2_SYSTEM_SURFACES_AND_ENTRYPOINTS.md, reports/REPORT_3_DATA_AND_SCHEMA_FACTS.md, reports/REPORT_4_TEST_AND_RUNTIME_STATUS.md, reports/REPORT_5_GOVERNANCE_INTEGRITY_CHECK.md]
conflicts_with: []
tags: [mvp, plan, planning, context]
---

# MVP Plan — Current State to Locked MVP

This plan enumerates the work required to move from the current, evidenced state to the locked MVP capability definition. It is derived from the gap analysis and the five reports, and is organized by MVP capability gaps only.

---

## Scope

Gaps requiring work (from current evidence):
- MVP-5 — State continuity requires explicit reaffirmation (Partially Implemented)
- MVP-6 — Evidence may be referenced but never evaluated (Not Implemented)
- MVP-8 — Explicit, downstream-only Guild exhaust export (Partially Implemented)
- MVP-10 — Absence of action is a preserved, inspectable fact (Not Implemented)

Already implemented and out of scope:
- MVP-1, MVP-2, MVP-3, MVP-4, MVP-7, MVP-9, MVP-11

---

## Workstreams and Deliverables

### MVP-5 — Explicit reaffirmation continuity
- Define and implement time-in-state persistence and display rules that prevent silence from implying continuity.
- Add data/query support for time-in-state accumulation without reaffirmation.
- Add tests that verify continuity rules and time-in-state behavior.
- Update reports to capture evidence of enforcement and visibility.

### MVP-6 — Evidence references are inert
- Extend state declarations to allow optional references to Cutter Ledger records or Ops artifacts.
- Ensure references are stored as inert metadata with no evaluation or derived logic.
- Add tests that assert references do not alter system behavior.
- Update reports to capture evidence of reference support and inert handling.

### MVP-8 — Guild exhaust export constraints
- Validate export is raw, additive exhaust with preserved provenance and explicit human initiation.
- Add tests or verification steps for export payload invariants and initiation semantics.
- Update reports to capture evidence of raw, additive, downstream-only export behavior.

### MVP-10 — Absence-of-action preservation
- Define explicit surfacing of elapsed time without action as a durable, inspectable fact.
- Add data/query mechanisms that expose absence-of-action without interpretation.
- Add tests that confirm absence-of-action visibility without judgment.
- Update reports to capture evidence of preserved absence-of-action facts.

---

## Evidence Update Protocol

For each workstream:
- Implement capability changes.
- Update test coverage to demonstrate the success conditions.
- Refresh reports 1–4 with direct file/test evidence.
- Update MVP Gap Analysis status accordingly.

