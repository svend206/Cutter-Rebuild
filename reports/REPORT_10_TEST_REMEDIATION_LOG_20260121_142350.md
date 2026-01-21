---
doc_id: report_test_remediation_log_20260121_142350
doc_type: context
status: active
version: 1.0
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [tests/, scripts/]
conflicts_with: []
tags: [report, tests, remediation, context]
---

# REPORT 10 — TEST REMEDIATION LOG

## Baseline Test Run

- Command: `python -m unittest`
- Result: FAILED (errors=13, failures=8, skipped=5)

## Rolling Fix Log

- Import/module errors:
  - Fix: Added root wrappers for `genesis_hash`, `pdf_generator`, `pricing_engine`.
  - Fix: Added `validate_genesis_hash` to `ops_layer/genesis_hash.py`.
  - Result: Import errors cleared.
- Schema mismatch (evidence_refs_json):
  - Fix: Added `evidence_refs_json` to State Ledger test/demo schema definitions.
  - Fix: Added migration-safe column addition in `database.initialize_database()`.
  - Result: `no such column: evidence_refs_json` cleared.
- Temp DB cleanup / stale data:
  - Fix: `reset_db.create_fresh_db` now removes existing test DB files before creation.
  - Result: Export tests no longer see stale rows.
- /api/system/health 400:
  - Fix: Default `system_health_endpoint` to planning mode when `ops_mode` missing.
  - Result: Endpoint returns metrics without 400.
- /export_guild_packet 500/400:
  - Fix: Use temp dir for export file in test mode.
  - Fix: Use dynamic DB path resolution in `database.get_connection()`.
  - Result: Export test passes.
- loop1 ritual demo output count:
  - Fix: Suppressed DB mode stdout during demo script init.
  - Result: Demo emits only JSON outputs.
- state time-in-state flakiness:
  - Fix: `state_ledger.queries` now resolves DB path per call.
  - Fix: Test resets `TEST_DB_PATH` before export/time-in-state calls.
  - Result: Full suite stable.

## Final Test Run

- Command: `python -m unittest`
- Result: OK (skipped=5)
