---
doc_id: report_current_capability_inventory
doc_type: context
status: active
version: 1.0
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - ops_layer/app.py
  - tests/
conflicts_with: []
tags: [report, capability, context]
---

# REPORT 1 — CURRENT CAPABILITY INVENTORY (FACTUAL)

- System can generate quotes from uploaded 3D files (user-visible).
  Evidence: `ops_layer/app.py` (`/quote`), `tests/test_integration.py`
- System can confirm units after upload (user-visible).
  Evidence: `ops_layer/app.py` (`/quote/confirm-units`)
- System can recalculate pricing from inputs (user-visible).
  Evidence: `ops_layer/app.py` (`/recalculate`)
- System can create manual (Napkin Mode) quotes (user-visible).
  Evidence: `ops_layer/app.py` (`/manual_quote`)
- System can save quotes (user-visible).
  Evidence: `ops_layer/app.py` (`/save_quote`)
- System can generate quote PDFs (user-visible).
  Evidence: `ops_layer/app.py` (`/api/quote/<id>/pdf`), `tests/test_pdf_generation.py`
- System can generate traveler PDFs (user-visible).
  Evidence: `ops_layer/app.py` (`/api/quote/<id>/traveler`), `tests/test_qr_codes.py`
- System can record win/loss outcomes (user-visible).
  Evidence: `ops_layer/app.py` (`/api/quote/<id>/outcome`, `/api/quote/<id>/outcome/wizard`), `tests/test_quote_lifecycle_events.py`
- System can update quote status (user-visible).
  Evidence: `ops_layer/app.py` (`/api/quote/<id>/update_status`)
- System can retrieve quote details (user-visible).
  Evidence: `ops_layer/app.py` (`/api/quote/<id>`), `tests/test_quote_lifecycle_events.py`
- System can list quote history (user-visible).
  Evidence: `ops_layer/app.py` (`/history`)
- System can soft-delete quotes (user-visible).
  Evidence: `ops_layer/app.py` (`/delete_quote/<id>`), `tests/test_soft_delete.py`
- System can provide pattern suggestions from local history (user-visible).
  Evidence: `ops_layer/app.py` (`/api/pattern_suggestions`), `tests/test_integration.py`
- System can convert units and dimensions (internal/API).
  Evidence: `ops_layer/app.py` (`/api/convert_units`), `tests/test_unit_conversion.py`
- System can manage customer records (user-visible/API).
  Evidence: `ops_layer/app.py` (`/api/customers`, `/api/customer/<id>`), `tests/test_customers_backend.py`
- System can manage contact records (user-visible/API).
  Evidence: `ops_layer/app.py` (`/api/contacts/search`, `/api/customer/<id>/contact`, `/api/contact/<id>`), `tests/test_customers_backend.py`
- System can manage variance tags (user-visible/API).
  Evidence: `ops_layer/app.py` (`/tags`, `/tags/new`, `/tags/<id>`), `tests/test_price_breaks.py`
- System can provide material list (user-visible/API).
  Evidence: `ops_layer/app.py` (`/materials`)
- System can check quote ID availability (user-visible/API).
  Evidence: `ops_layer/app.py` (`/check_quote_id/<id>`)
- System can export Guild packet (user-visible/API).
  Evidence: `ops_layer/app.py` (`/export_guild_packet`), `tests/test_query_cli_readonly.py`
- System can report pending exports count (user-visible/API).
  Evidence: `ops_layer/app.py` (`/pending_exports`)
- System can emit and query operational exhaust (internal/API).
  Evidence: `ops_layer/app.py` (`/ops/carrier_handoff`, `/api/cutter/dwell-vs-expectation`)
- System can query State Ledger open deadlines (internal/API).
  Evidence: `ops_layer/app.py` (`/api/state/open-deadlines`)
- System can query State Ledger open response deadlines (internal/API).
  Evidence: `ops_layer/app.py` (`/api/state/open-response-deadlines`)
- System can run database reset and bootstrap (internal/script).
  Evidence: `scripts/reset_db.py`
- System can run ledger query CLI (internal/script).
  Evidence: `scripts/ledger_query_cli.py`, `tests/test_ledger_query_cli.py`
- System can run weekly ritual visibility report (internal/script).
  Evidence: `scripts/weekly_ritual.py`, `tests/test_weekly_ritual.py`
- System can run end-to-end demo (internal/script).
  Evidence: `scripts/demo_end_to_end.py`, `tests/test_demo_end_to_end.py`
