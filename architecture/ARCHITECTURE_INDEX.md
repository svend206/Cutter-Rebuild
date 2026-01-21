---
doc_id: architecture_index
doc_type: context
status: active
version: 1.8
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [architecture, context]
---

# Architecture Memory

Descriptive system memory only. No authority.

## Modules
- Ops Layer (work execution UI + logic)
- Cutter Ledger (append-only operational exhaust)
- State Ledger (explicit human recognition)
- Guild (separate product surface)

## Navigation
- `architecture/NAVIGATION_INDEX.md`
- `architecture/NAVIGATION_DRIFT_REPORT.md`
- `packs/ARCHITECT.md`
- `packs/BUILDER.md`
- `packs/UI_UX.md`
- `packs/OPS.md`
- `packs/CUTTER.md`
- `packs/STATE.md`
- `packs/GUILD.md`

## Features
- RFQ-first gating (Ops)
- Glass-box pricing (Ops)
- Variance attribution (Ops)
- Manual Guild export (Ops Admin)

## Data Models
- Database is SQLite with WAL (authoritative in code/migrations)
- Table families by prefix: `ops__*`, `cutter__*`, `state__*`
- Human-readable reference: `architecture/SCHEMA_REFERENCE.md`

## Key Decisions (Non-Constitutional)
- Nodes are distinct UI surfaces (Ops, Cutter Ledger, State Ledger, Guild)

## Planning (Non-Authoritative)
- `bootstrap/MVP Capability Definition.md`
- `context/MVP_CAPABILITIES_LOCKED.md`
- `context/MVP_V2_REBASELINE_DECLARATION.md`
- `context/MVP_V2_COVERAGE_ASSERTION_TABLE.md`
- `context/UI_REALITY_REPORT.md`
- `context/UI_SUFFICIENCY_MATRIX_FOR_MVP.md`
- `context/PLAN_INPUTS_GAP_MAP.md`
- `context/MVP_VERIFICATION_GAP_ANALYSIS.md`
- `context/UI_Verification_Loop_Checklist.md`
- `context/UI_VERIFICATION_SPEC_MVP-1.md`
- `context/UI_VERIFICATION_SPEC_MVP-12.md`
- `context/UI_VERIFICATION_SPEC_MVP-13.md`
- `context/UI_VERIFICATION_SPEC_MVP-14.md`
- `context/UI_VERIFICATION_SPEC_MVP-15.md`
- `context/MVP_15_REFUSAL_SURFACE_VERIFICATION.md`
- Archived MVP planning docs moved to `archive/`

## Manifesto (Non-Authoritative)
- `context/manifesto/CORE_MANIFESTO.md`
- `context/manifesto/# Cannot Outsource Risk.md`
- `context/manifesto/think_different.md`
- `context/manifesto/Why Cutter.md`
