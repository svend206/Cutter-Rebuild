---
doc_id: architecture_index
doc_type: context
status: active
version: 1.3
date: 2026-01-18
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
- `architecture/MVP Gap Analysis.md`
- `architecture/MVP Plan.md`
