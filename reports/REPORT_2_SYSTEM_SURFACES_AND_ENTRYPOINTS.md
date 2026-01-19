---
doc_id: report_system_surfaces_entrypoints
doc_type: context
status: active
version: 1.2
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - app.py
  - ops_layer/app.py
  - scripts/
conflicts_with: []
tags: [report, entrypoints, context]
---

# REPORT 2 — SYSTEM SURFACES & ENTRYPOINTS

## Canonical App Entrypoint
- `app.py` — root entrypoint shim.
  Evidence: `app.py` imports `ops_layer.app` and runs `app.run(...)`.

## UI Entrypoints
- `/` — main UI page.
  Evidence: `ops_layer/app.py` (`@app.route('/')`)

## Health / System Endpoints
- `/health` — health check.
  Evidence: `ops_layer/app.py` (`@app.route('/health')`)
- `/api/system/health` — system telemetry.
  Evidence: `ops_layer/app.py` (`@app.route('/api/system/health')`, `require_ops_mode`)

## API Entrypoints (Representative Set)
- Quote creation: `/quote`, `/manual_quote`, `/save_quote`.
  Evidence: `ops_layer/app.py`
- Quote retrieval and PDF: `/api/quote/<id>`, `/api/quote/<id>/pdf`, `/api/quote/<id>/traveler`.
  Evidence: `ops_layer/app.py`
- Outcomes/status: `/api/quote/<id>/outcome`, `/api/quote/<id>/outcome/wizard`, `/api/quote/<id>/update_status`.
  Evidence: `ops_layer/app.py`
- Customers/contacts: `/api/customers`, `/api/customers/search`, `/api/contacts/search`, `/api/customer/<id>`, `/api/customer/<id>/contact`, `/api/contact/<id>`.
  Evidence: `ops_layer/app.py`
- Tags: `/tags`, `/api/tags`, `/tags/new`, `/tags/<id>`.
  Evidence: `ops_layer/app.py`
- Pattern suggestions: `/api/pattern_suggestions`.
  Evidence: `ops_layer/app.py` (blocked in execution mode)
- Ledger queries: `/api/state/open-deadlines`, `/api/state/open-response-deadlines`, `/api/cutter/dwell-vs-expectation`.
  Evidence: `ops_layer/app.py`
- Guild export: `/export_guild_packet` (POST, actor_ref required), `/pending_exports`.
  Evidence: `ops_layer/app.py`

## Script Entrypoints
- Server start/stop: `scripts/start_server.ps1`, `scripts/kill_server.ps1`.
  Evidence: `scripts/start_server.ps1`, `scripts/kill_server.ps1`
- Database reset: `scripts/reset_db.py`.
  Evidence: `scripts/reset_db.py`
- Ledger query CLI: `scripts/ledger_query_cli.py`.
  Evidence: `scripts/ledger_query_cli.py`
- Weekly ritual: `scripts/weekly_ritual.py`.
  Evidence: `scripts/weekly_ritual.py`
- End-to-end demo: `scripts/demo_end_to_end.py`.
  Evidence: `scripts/demo_end_to_end.py`
- State ledger demo: `scripts/state_ledger_demo.py`.
  Evidence: `scripts/state_ledger_demo.py`
- Loop ritual demo: `scripts/loop1_ritual_demo.py`.
  Evidence: `scripts/loop1_ritual_demo.py`
- Baseline declarations: `scripts/baseline_declarations.py`.
  Evidence: `scripts/baseline_declarations.py`
- Inspect state schema: `scripts/inspect_state_schema.py`.
  Evidence: `scripts/inspect_state_schema.py`
- Preflight smoke test: `scripts/preflight_smoke_test.py`.
  Evidence: `scripts/preflight_smoke_test.py`
- Verify event emission: `verify_event_emission.py`.
  Evidence: `verify_event_emission.py`

## Background / Scheduled Processes
- None found in repo (no scheduler or cron configuration present).
