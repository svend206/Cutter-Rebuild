---
doc_id: report_test_artifact_hygiene_20260121_162931
doc_type: context
status: active
version: 1.0
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/BOOT_CONTRACT.md]
conflicts_with: []
tags: [report, hygiene, tests, context]
---

# REPORT 27 — TEST ARTIFACT HYGIENE

## Git Status (Before)

```
 M integrator/INTEGRATOR_HOME.md
?? tests/test_mvp12_reconciliation.db
?? tests/test_mvp13_execution_continuity.db
?? tests/test_mvp14_exhaust_byproduct.db
?? tests/test_mvp15_refusal.db
?? tests/tmp_state_time.db
```

## Deleted Artifacts

- `tests/test_mvp12_reconciliation.db`
- `tests/test_mvp13_execution_continuity.db`
- `tests/test_mvp14_exhaust_byproduct.db`
- `tests/test_mvp15_refusal.db`
- `tests/tmp_state_time.db`

## .gitignore Updates

- Added:
  - `tests/*.db`
  - `tests/tmp*.db`
  - `tests/**/tmp*.db`

## Test DB Path Changes

- Tests now default to temp directory paths for `TEST_DB_PATH` in:
  - `tests/test_app_entrypoint.py`
  - `tests/test_guild_export_payload.py`
  - `tests/test_mvp12_reconciliation.py`
  - `tests/test_mvp13_execution_continuity.py`
  - `tests/test_mvp14_exhaust_byproduct.py`
  - `tests/test_mvp15_refusal.py`
  - `tests/test_ops_mode_guard.py`

## Git Status (After)

```
 M .gitignore
 M DIRECTORY.md
 M integrator/INTEGRATOR_HOME.md
 M tests/test_app_entrypoint.py
 M tests/test_guild_export_payload.py
 M tests/test_mvp12_reconciliation.py
 M tests/test_mvp13_execution_continuity.py
 M tests/test_mvp14_exhaust_byproduct.py
 M tests/test_mvp15_refusal.py
 M tests/test_ops_mode_guard.py
?? reports/REPORT_27_TEST_ARTIFACT_HYGIENE_20260121_162931.md
```

## Gates / Tests

- `python scripts/audit_gate.py` — PASS
- `python -m unittest` — PASS (113 tests, 5 skipped)
