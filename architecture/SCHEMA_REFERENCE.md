---
doc_id: schema_reference
doc_type: context
status: active
version: 1.0
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - database.py
  - migrations/
conflicts_with: []
tags: [schema, reference, context]
---

# Schema Reference (Non-Authoritative)

This document is a human-readable reference only.  
**Code + migrations are authoritative.**

## Scope
High-level structure of the operational database as reflected in code and migrations.

## Table Families (By Prefix)
- `ops__*` — operational work records (quotes, parts, customers, contacts, tags, outcomes).
- `cutter__*` — append-only operational exhaust events.
- `state__*` — explicit human recognition (entities, owners, declarations).

## Core Invariants (Descriptive)
- Cutter Ledger and State Ledger tables are append-only.
- Ops tables are mutable operational records.
- State recognition is explicit and attributed to a human owner.

## References (Authoritative Sources)
- `database.py`
- `migrations/`
