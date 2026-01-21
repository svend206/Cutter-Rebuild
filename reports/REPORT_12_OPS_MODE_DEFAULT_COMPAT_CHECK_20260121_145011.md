---
doc_id: report_ops_mode_default_compat_check_20260121_145011
doc_type: context
status: active
version: 1.0
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [bootstrap/MVP Capability Definition.md, constitution/ops_layer/OPS_CANON.md, ops_layer/mode_seperation.md, constitution/CORE_QUERY_LAYER_RULES.md]
conflicts_with: []
tags: [report, ops_mode, compliance, context]
---

# REPORT 12 — OPS MODE DEFAULT COMPAT CHECK

## 1) Behavior Location (Code)

- Default behavior implemented in `ops_layer/app.py`:
  - Function: `system_health_endpoint()`
  - Prior logic: `mode = get_ops_mode() or "planning"`

## 2) UI/Surface Callers (Code-Only)

- No references to `/api/system/health` found in:
  - `ops_layer/static/js/modules/api.js`
  - `ops_layer/static/js/main.js`
- No additional UI callers identified in code reviewed.

## 3) Endpoint Payload Characteristics

- Returns metrics and system aggregates:
  - `metrics`: CPU percent, memory usage, disk free, DB size
  - `system_info`: process ID, platform, CPU count

## 4) Constitutional/MVP Compliance (Doc-Cited)

### MVP-9 — Document-Governed, Non-Inventive
Source: `bootstrap/MVP Capability Definition.md` → “MVP-9 — System authority is document-governed and non-inventive”

- Requirement: enforced constraints must trace to constitution/spec/decision log.
- Finding: A default to planning mode is not explicitly authorized in authoritative docs.
- Status: FAIL (prior default).

### MVP-11 — Execution vs Planning Separation
Sources:
- `bootstrap/MVP Capability Definition.md` → “MVP-11 — Ops enforces separation of execution and planning modes”
- `ops_layer/mode_seperation.md` → “Mode Separation”
- `constitution/ops_layer/OPS_CANON.md` → “O6 — Execution and Planning Are Separate”

- Requirement: mode switching must be explicit, intentional, auditable; system must not silently cross modes.
- Finding: defaulting to planning when ops_mode is absent is a silent mode selection.
- Status: FAIL (prior default).

### Query/UX Constraints
Source: `constitution/CORE_QUERY_LAYER_RULES.md` → “Allowed Query Operations”

- Requirement: aggregates are permitted only when the instance set is directly accessible.
- Health endpoint returns system metrics; no instance set is exposed.
- Compliance depends on explicit, auditable planning-mode intent.
- Status: FAIL (prior default due to silent planning selection).

## 5) Remediation Decision (Minimal)

- Selected remediation: **Fail closed** — require explicit ops_mode for `/api/system/health`.
- Rationale: required by explicit mode separation (no silent mode selection).

## 6) Remediation Applied

- `ops_layer/app.py` → `system_health_endpoint()` now uses `require_ops_mode()` and returns an explicit error when missing.
- `tests/test_app_entrypoint.py` updated to supply `X-Ops-Mode: planning` for the health endpoint call.

## 7) Post-Remediation Compliance

- MVP-9: PASS (explicit mode requirement; no undocumented default).
- MVP-11: PASS (explicit, auditable mode selection).
- CORE_QUERY_LAYER_RULES: PASS (planning-only metrics now require explicit mode).

## 8) Gate/Test Results (Post-Remediation)

- Audit gate: PASS
  - Command: `python scripts/audit_gate.py`
  - Output: LOC delta 0; Files changed (non-canon) 0; OK: audit not required
- Tests: PASS (skipped=5)
  - Command: `python -m unittest`
