---
doc_id: report_mvp12_verification_evidence_20260121_153518
doc_type: context
status: active
version: 1.1
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [context/MVP_CAPABILITIES_LOCKED.md, constitution/CORE_QUERY_LAYER_RULES.md]
conflicts_with: []
tags: [report, mvp12, evidence, context]
---

# REPORT 15 — MVP-12 VERIFICATION EVIDENCE

## What Changed

- `ops_layer/app.py`: Reconciliation endpoint now requires `predicate_ref` and treats `predicate_text` as optional display metadata.
- `database.py`: `ops__reconciliations` now stores `predicate_ref` as the binding key; `predicate_text` is nullable.
- `scripts/reset_db.py`: Updated reconciliation schema for test DBs.
- `tests/test_mvp12_reconciliation.py`: Expanded tests for stable predicate binding and optional predicate text.

## MVP-12 Success Condition Mapping

- **Explicit human reconciliation**: `POST /api/reconcile` requires `actor_ref` and explicit payload fields.
- **Query/report scoped**: Requires `scope_ref` + `scope_kind` (`query` or `report`) + `predicate_ref`.
- **Predicate text optional**: `predicate_text` is display-only metadata and may be absent.
- **Non-blocking**: Reconciliation is a standalone record; no execution flow is gated.
- **No global reconciliation state**: Records are scoped entries only; no global flag.
- **Auditable**: Stored with actor + timestamp + scope + predicate.

## Tests and Results

- `tests.test_mvp12_reconciliation.TestMVP12Reconciliation.test_reconciliation_records_query_scoped_entry` — PASS
- `tests.test_mvp12_reconciliation.TestMVP12Reconciliation.test_reconciliation_allows_missing_predicate_text` — PASS
- `tests.test_mvp12_reconciliation.TestMVP12Reconciliation.test_reconciliation_binding_ignores_predicate_text_variance` — PASS
- `python -m unittest` — PASS (skipped=5)
- `python scripts/audit_gate.py` — PASS

## Residual Gaps / Known Limits

- Legacy reconciliation rows are backfilled with `predicate_ref = predicate_text` during schema rebuild.
