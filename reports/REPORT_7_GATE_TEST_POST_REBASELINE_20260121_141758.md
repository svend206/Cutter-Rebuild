---
doc_id: report_gate_test_post_rebaseline_20260121_141758
doc_type: context
status: active
version: 1.0
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [report, gates, tests, context]
---

# REPORT 7 — GATE + TEST RESULTS (POST-REBASELINE)

## Audit Gate

- Command: `python scripts/audit_gate.py`
- Result: FAILED
- Reasons:
  - LOC delta 3345 > 500
  - 48 files changed outside canon >= 10

## Unit Tests

- Command: `python -m unittest`
- Result: FAILED (errors=13, failures=8, skipped=5)

### Failure Classification

- Governance/config issues:
  - None detected.
- Test brittleness / environment:
  - `tests.test_genesis_hash` import error: `ModuleNotFoundError: No module named 'genesis_hash'`
  - Multiple SQLite errors: `no such column: evidence_refs_json` in demo and query tests
  - PermissionError on temp DB file cleanup in identifier validation tests
- Potential regression:
  - `/api/system/health` returning 400 instead of 200 in `tests.test_app_entrypoint`
  - `/export_guild_packet` returning 500 in `tests.test_guild_export_payload`

## Doc-Only Fixes Applied

- None. (Failures are not documentation/registry issues.)
