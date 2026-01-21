---
doc_id: ui_sufficiency_matrix_for_mvp
doc_type: context
status: active
version: 1.1
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [ui, mvp, matrix, context]
---

# UI Sufficiency Matrix for MVP (Verification Needs)

| MVP Capability | What must be observable in UI to verify enforcement (minimum) | Currently observable in UI? (Yes/No/Unknown) | Evidence (paths/tests/routes) |
| --- | --- | --- | --- |
| MVP-1 Ops can perform work and emit exhaust | UI must show operational actions and a UI-visible exhaust record view with actor/timestamp values. | No | `ops_layer/templates/index.html` (109-236), `ops_layer/static/js/modules/sidebar.js` (220-276) |
| MVP-2 Cutter Ledger preserves demonstrated operational reality | UI must provide a ledger view showing chronological exhaust persistence. | No | `ops_layer/templates/index.html` (109-1569) |
| MVP-3 Cutter Ledger read-only meaning | UI must show ledger records without evaluative labels/fields in the ledger view. | No | `ops_layer/templates/index.html` (109-1569) |
| MVP-4 State Ledger supports explicit human recognition | UI must allow explicit state declaration entry with actor identity and timestamps. | No | `ops_layer/templates/index.html` (109-1569) |
| MVP-5 State continuity requires explicit reaffirmation | UI must show time-in-state or reaffirmation history for state declarations. | No | `ops_layer/templates/index.html` (109-1569) |
| MVP-6 Evidence referenced but inert | UI must allow attaching evidence references and show them as inert metadata. | No | `ops_layer/templates/index.html` (109-1569) |
| MVP-7 Layer separation enforced | UI must show that Ops actions do not create state entries and no automated transitions appear in UI. | Unknown | `context/UI_REALITY_REPORT.md` |
| MVP-8 Explicit, downstream-only Guild export | UI must provide an explicit export action and show export results without feedback into Ops/State/Ledger UI. | No | `ops_layer/templates/index.html` (109-1569) |
| MVP-9 Document-governed authority | UI must expose authoritative document registry or constraints as UI-verifiable references. | No | `DIRECTORY.md` |
| MVP-10 Absence of action preserved | UI must show elapsed time since last action in at least one operational/state context. | No | `ops_layer/templates/index.html` (125-145) |
| MVP-11 Ops execution/planning separation | UI must expose ops mode state and explicit switching, with planning signals suppressed in execution. | Unknown | `ops_layer/static/js/modules/state.js` (17-47), `ops_layer/templates/index.html` (414-483), `context/UI_REALITY_REPORT.md` |
| MVP-12 Reconciliation explicit, query-dependent, non-blocking | UI must show reconciliation scoped to a specific report or question, without blocking execution. | No | `context/UI_REALITY_REPORT.md` |
| MVP-13 Execution continuous and never gated | UI must show execution actions are available regardless of reconciliation or planning state. | Unknown | `context/UI_REALITY_REPORT.md` |
| MVP-14 Exhaust capture byproduct, not obligation | UI must allow completing execution flows without mandatory explanations or annotations. | Unknown | `context/UI_REALITY_REPORT.md` |
| MVP-15 Explicit refusal of automated harm/blame computation | UI must show explicit refusal when automated harm/blame computation is attempted. | No | `context/UI_REALITY_REPORT.md` |
