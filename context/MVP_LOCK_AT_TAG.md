---
doc_id: mvp_lock_at_tag_20260122
doc_type: context
status: active
version: 1.0
date: 2026-01-22
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [context/MVP_CAPABILITIES_LOCKED.md]
conflicts_with: []
tags: [mvp, lock, checkpoint, context]
---

# MVP Lock at Tag

## Tag
- Name: mvp-locked-all-green-2026-01-22
- Commit: 23be9b33de5f2a0aa58fe2d73ee024d63a01f460
- Date: 2026-01-22

## MVP Evidence Ledger (All Failure Modes Tested)
| MVP | Capability name (verbatim) | Proof type | Evidence location | Last verified | Failure mode tested? |
|---|---|---|---|---|---|
| MVP-1 | Ops can perform work and emit exhaust | automated test | `tests/test_quote_lifecycle_events.py::test_no_exhaust_on_refused_ops_action` | 23be9b3 | yes |
| MVP-2 | Cutter Ledger preserves demonstrated operational reality | automated test | `tests/test_operational_events.py::test_trigger_prevents_update` | 23be9b3 | yes |
| MVP-3 | Cutter Ledger is read-only with respect to meaning | automated test | `tests/test_operational_events.py::test_emit_event_rejects_evaluative_language` | 23be9b3 | yes |
| MVP-4 | State Ledger supports explicit human recognition | automated test | `tests/test_phase5_state_ledger.py::TestMVP4ExplicitRecognition.test_no_implicit_declaration_created` | 23be9b3 | yes |
| MVP-5 | State continuity requires explicit reaffirmation | automated test | `tests/test_state_time_in_state.py::test_silence_does_not_create_new_declaration` | 23be9b3 | yes |
| MVP-6 | Evidence may be referenced but never evaluated | automated test | `tests/test_state_evidence_refs.py::test_evidence_presence_does_not_change_behavior` | 23be9b3 | yes |
| MVP-7 | Separation between Ops, Cutter Ledger, and State Ledger is enforced | automated test | `tests/test_phase5_state_ledger.py::TestMVP7SeparationEnforcement.test_state_declaration_refuses_in_execution_mode` | 23be9b3 | yes |
| MVP-8 | Explicit, downstream-only Guild exhaust export | automated test | `tests/test_guild_export_payload.py::test_export_payload_includes_provenance` | 23be9b3 | yes |
| MVP-9 | System authority is document-governed and non-inventive | automated test | `tests/test_query_cli_readonly.py::test_cli_does_not_import_reset_modules` | 23be9b3 | yes |
| MVP-10 | Absence of action is a preserved, inspectable fact | automated test | `tests/test_phase5_state_ledger.py::test_ds5_deferred_recognition` | 23be9b3 | yes |
| MVP-11 | Ops enforces separation of execution and planning modes | automated test | `tests/test_ops_mode_guard.py::test_execution_mode_strips_metrics` | 23be9b3 | yes |
| MVP-12 | Reconciliation is explicit, query-dependent, and non-blocking | automated test | `tests/test_mvp12_reconciliation.py::test_reconciliation_does_not_block_execution` | 23be9b3 | yes |
| MVP-13 | Execution is continuous and never gated | automated test | `tests/test_mvp13_execution_continuity.py::test_execution_continues_with_reconciliation_present` | 23be9b3 | yes |
| MVP-14 | Exhaust capture is a byproduct, not an obligation | automated test | `tests/test_mvp14_exhaust_byproduct.py::test_save_quote_succeeds_without_explanations` | 23be9b3 | yes |
| MVP-15 | The system explicitly refuses automated harm and blame computation | explicit refusal | `tests/test_mvp15_refusal.py::test_refuses_prohibited_query` | 23be9b3 | yes |

MVP behavior is frozen at this tag. Any change that alters MVP behavior requires an explicit unlock artifact.
