---
doc_id: report_test_runtime_status
doc_type: context
status: active
version: 1.1
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - tests/
  - ops_layer/app.py
  - database.py
  - scripts/reset_db.py
conflicts_with: []
tags: [report, tests, runtime, context]
---

# REPORT 4 — TEST & RUNTIME STATUS

## Test Coverage That Exists (Evidence = test files)
- App entrypoint + health endpoints.
  Evidence: `tests/test_app_entrypoint.py`
- Pricing algorithms and price breaks.
  Evidence: `tests/test_pricing_algorithms.py`, `tests/test_price_breaks.py`
- Genesis hash behavior.
  Evidence: `tests/test_genesis_hash.py`
- Unit conversion.
  Evidence: `tests/test_unit_conversion.py`
- Quote lifecycle and outcomes.
  Evidence: `tests/test_quote_lifecycle_events.py`
- Customer/contact backend.
  Evidence: `tests/test_customers_backend.py`
- PDF generation.
  Evidence: `tests/test_pdf_generation.py`
- Operational event emission/query behavior.
  Evidence: `tests/test_operational_events.py`, `tests/test_query_cli_readonly.py`
- Ops mode execution guard.
  Evidence: `tests/test_ops_mode_guard.py`
- State ledger behaviors.
  Evidence: `tests/test_state_schema.py`, `tests/test_phase5_state_ledger.py`, `tests/test_phase5e_declaration_kind.py`
- Integration and demo flows.
  Evidence: `tests/test_integration.py`, `tests/test_demo_end_to_end.py`, `tests/test_frontend_integration.py`

## Runtime Assumptions (Evidence = code)
- `cutter.db` exists for production runtime.
  Evidence: `database.py` (`PROD_DB_PATH`)
- `TEST_DB_PATH` required for test runs and guarded scripts.
  Evidence: `database.py` (`validate_db_mode`, `require_test_db`)
- Upload folder at `C:\\cutter_assets`.
  Evidence: `ops_layer/app.py` (`app.config['UPLOAD_FOLDER']`)
- Python deps used at runtime: `flask`, `trimesh`, `psutil`.
  Evidence: `ops_layer/app.py` imports

## Boot + Health Endpoint Verification (Evidence = test)
- `/health` returns `{status: "ok"}`.
  Evidence: `tests/test_app_entrypoint.py`, `ops_layer/app.py`
- `/api/system/health` requires ops_mode and strips metrics in execution mode.
  Evidence: `tests/test_ops_mode_guard.py`, `ops_layer/app.py`
