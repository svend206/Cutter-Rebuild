---
doc_id: report_data_schema_facts
doc_type: context
status: active
version: 1.3
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - database.py
  - migrations/
  - scripts/reset_db.py
  - ops_layer/preflight.py
conflicts_with: []
tags: [report, schema, context]
---

# REPORT 3 — DATA & SCHEMA FACTS

## Databases in Use
- SQLite database at `cutter.db`.
  Evidence: `database.py` (`PROD_DB_PATH`)

## Core Table Families (By Prefix)
- `ops__*` — operational records (materials, shop config, quote history, customers, contacts, parts, quotes, custom tags, outcomes).
  Evidence: `database.py` (`initialize_database`)
- `cutter__*` — append-only operational exhaust events.
  Evidence: `database.py`, `scripts/reset_db.py` (trigger creation)
- `state__*` — explicit human recognition (entities, recognition owners, declarations).
  Evidence: `database.py`, `scripts/reset_db.py` (trigger creation)

## Key Invariants Enforced
- WAL mode on every connection.
  Evidence: `database.py` (`get_connection` uses `PRAGMA journal_mode=WAL`)
- Append-only enforcement for `cutter__events` and `state__declarations` via triggers.
  Evidence: `scripts/reset_db.py` (CREATE TRIGGER statements), `ops_layer/preflight.py` (required trigger checks)
- Preflight fails if required tables or triggers are missing.
  Evidence: `ops_layer/preflight.py` (`REQUIRED_TABLES`, `REQUIRED_TRIGGERS`)
- Evidence references are stored as inert metadata.
  Evidence: `scripts/reset_db.py` (evidence_refs_json), `state_ledger/boundary.py`

## Derived State Views
- `view_ds1_persistent_continuity` — reaffirmation streaks since last reclassification.
  Evidence: `scripts/reset_db.py`, `state_ledger/queries.py`
- `view_ds2_unowned_recognition` — entities without a current owner.
  Evidence: `scripts/reset_db.py`, `state_ledger/boundary.py`
- `view_ds5_deferred_recognition` — entities past cadence window.
  Evidence: `scripts/reset_db.py`, `state_ledger/boundary.py`
- `view_state_time_in_state` — latest declaration + elapsed time.
  Evidence: `scripts/reset_db.py`, `state_ledger/queries.py`

## Derived Ops Views
- `view_ops_unclosed_quotes` — quotes without outcomes + elapsed time.
  Evidence: `scripts/reset_db.py`, `database.py` (`get_unclosed_quotes`)

## Schema Authority
- Authoritative schema lives in `database.py` and `migrations/`.
  Evidence: `database.py`, `migrations/*.py`
