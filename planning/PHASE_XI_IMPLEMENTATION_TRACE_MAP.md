---
doc_id: phase_xi_implementation_trace_map
doc_type: spec
status: draft
version: 1.1
date: 2026-01-26
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - constitution/CONSTITUTION_AUTHORITY.md
  - boot/BOOT_CONTRACT.md
  - boot/PROJECT_PHASE_CONSTITUTION.md
  - integrator/INTEGRATOR_HOME.md
  - planning/PHASE_XI_WORK_CHARTER.md
  - planning/PHASE_XI_CONSTRAINT_COVERAGE_MATRIX.md
conflicts_with: []
tags: [phase, implementation, trace, map, spec]
---

# Phase XI Implementation Trace Map (Authoritative)

This document is traceability-only and definition-preserving.
It does not authorize implementation.

---

## EXPLICITLY UNIMPLEMENTED Constraints

| Trace ID | Constraint ID | Source (Artifact -> Section) | Constraint Text (Verbatim-Aligned) | Status | Implementation Surface (Placeholder Only) | Trace Type | Verification Method | Verification Evidence Placeholder | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TRACE-VI-OP-01 | VI-OP-01 | Phase VI Loop 1 -> Failure Modes | Failure must be visible; silent failure is forbidden. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | DISCLOSURE | integration test | tests/test_trace_vi_op_01.py |  |
| TRACE-VI-OP-03 | VI-OP-03 | Phase VI Loop 1 -> Failure Modes | Refusals must be explicit and visible when they occur. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | DISCLOSURE | integration test | tests/test_trace_vi_op_03.py |  |
| TRACE-VI-OP-04 | VI-OP-04 | Phase VI Loop 2 -> Refusal Semantics | Refusal must not be softened, bypassed, or replaced with partial success. | EXPLICITLY UNIMPLEMENTED | TBD_COMPONENT | ENFORCEMENT | property test | tests/test_trace_vi_op_04.py |  |
| TRACE-VII-NG-02 | VII-NG-02 | Phase VII Loop 1 -> Non-Guarantee Registry | Silence outside considered claims is unauthorized and must not be implied as assurance. | EXPLICITLY UNIMPLEMENTED | TBD_MODULE | COMMERCIAL | documentation lint rule | lint/trace_vii_ng_02.md |  |
| TRACE-VII-NG-03 | VII-NG-03 | Phase VII Loop 1 -> Claim Consideration Log | Denied or out-of-scope claims remain denied; none are elevated by behavior. | EXPLICITLY UNIMPLEMENTED | TBD_MODULE | COMMERCIAL | adversarial review checklist item | audit/trace_vii_ng_03.md |  |
| TRACE-VIII-VIS-04 | VIII-VIS-04 | Phase VIII Loop 2 -> Pattern 4 | The order of receipt and stored sequence of entries is visible as recorded. | EXPLICITLY UNIMPLEMENTED | TBD_STORAGE | RECORDING | integration test | tests/test_trace_viii_vis_04.py |  |
| TRACE-VIII-VIS-07 | VIII-VIS-07 | Phase VIII Loop 2 -> Pattern 7 | Claims of evidence without attachments are visible as such. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | DISCLOSURE | snapshot test | tests/test_trace_viii_vis_07.py |  |
| TRACE-VIII-VIS-08 | VIII-VIS-08 | Phase VIII Loop 2 -> Pattern 8 | Evidence substitutions remain visible (append-only provenance). | EXPLICITLY UNIMPLEMENTED | TBD_STORAGE | RECORDING | integration test | tests/test_trace_viii_vis_08.py |  |
| TRACE-VIII-VIS-11 | VIII-VIS-11 | Phase VIII Loop 2 -> Pattern 11 | Recorded consent indicators are visible as recorded fields. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | DISCLOSURE | snapshot test | tests/test_trace_viii_vis_11.py |  |
| TRACE-VIII-VIS-12 | VIII-VIS-12 | Phase VIII Loop 2 -> Pattern 12 | State transitions are visible as recorded transitions. | EXPLICITLY UNIMPLEMENTED | TBD_STORAGE | RECORDING | integration test | tests/test_trace_viii_vis_12.py |  |
| TRACE-VIII-VIS-13 | VIII-VIS-13 | Phase VIII Loop 2 -> Pattern 13 | Outcome fields are visible as recorded outcomes. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | DISCLOSURE | snapshot test | tests/test_trace_viii_vis_13.py |  |
| TRACE-VIII-VIS-14 | VIII-VIS-14 | Phase VIII Loop 2 -> Pattern 14 | Ownership assignments are visible as recorded. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | DISCLOSURE | snapshot test | tests/test_trace_viii_vis_14.py |  |
| TRACE-VIII-VIS-15 | VIII-VIS-15 | Phase VIII Loop 2 -> Pattern 15 | Evidence timing is visible via recorded timestamps. | EXPLICITLY UNIMPLEMENTED | TBD_STORAGE | RECORDING | integration test | tests/test_trace_viii_vis_15.py |  |
| TRACE-VIII-VIS-17 | VIII-VIS-17 | Phase VIII Loop 2 -> Pattern 17 | Export context (what subset was exported) is visible as a record. | EXPLICITLY UNIMPLEMENTED | TBD_STORAGE | RECORDING | integration test | tests/test_trace_viii_vis_17.py |  |
| TRACE-VIII-VIS-18 | VIII-VIS-18 | Phase VIII Loop 2 -> Pattern 18 | Aggregation inputs are visible (inputs recorded). | EXPLICITLY UNIMPLEMENTED | TBD_STORAGE | RECORDING | integration test | tests/test_trace_viii_vis_18.py |  |
| TRACE-VIII-VIS-19 | VIII-VIS-19 | Phase VIII Loop 2 -> Pattern 19 | Redaction choices are visible as recorded actions. | EXPLICITLY UNIMPLEMENTED | TBD_STORAGE | RECORDING | integration test | tests/test_trace_viii_vis_19.py |  |
| TRACE-VIII-VIS-20 | VIII-VIS-20 | Phase VIII Loop 2 -> Pattern 20 | Duplicate records are visible in storage. | EXPLICITLY UNIMPLEMENTED | TBD_STORAGE | RECORDING | integration test | tests/test_trace_viii_vis_20.py |  |
| TRACE-VIII-VIS-21 | VIII-VIS-21 | Phase VIII Loop 2 -> Pattern 21 | Record linkages are visible as recorded links. | EXPLICITLY UNIMPLEMENTED | TBD_STORAGE | RECORDING | integration test | tests/test_trace_viii_vis_21.py |  |
| TRACE-VIII-VIS-22 | VIII-VIS-22 | Phase VIII Loop 2 -> Pattern 22 | Unclaimed responsibility (empty fields) is visible. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | DISCLOSURE | snapshot test | tests/test_trace_viii_vis_22.py |  |
| TRACE-VIII-VIS-24 | VIII-VIS-24 | Phase VIII Loop 2 -> Pattern 24 | Absence of records is itself visible (silence is observable). | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | DISCLOSURE | snapshot test | tests/test_trace_viii_vis_24.py |  |
| TRACE-VIII-VIS-25 | VIII-VIS-25 | Phase VIII Loop 2 -> Pattern 25 | Partial disclosures are visible as disclosed subsets. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | DISCLOSURE | snapshot test | tests/test_trace_viii_vis_25.py |  |
| TRACE-IX-CLM-01 | IX-CLM-01 | Phase IX Prohibited Claim List | Forbidden terms (e.g., "ensures", "guarantees") must not appear in any commercial language. | EXPLICITLY UNIMPLEMENTED | TBD_MODULE | COMMERCIAL | documentation lint rule | lint/trace_ix_clm_01.md |  |
| TRACE-IX-CLM-02 | IX-CLM-02 | Phase IX Demonstration Constraint Statement | Demonstrations must not imply guarantees, detection, coverage, or safety. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | COMMERCIAL | adversarial review checklist item | audit/trace_ix_clm_02.md |  |
| TRACE-IX-CLM-03 | IX-CLM-03 | Phase IX Claim Consistency Check | Commercial statements must remain consistent with Phase VII zero-guarantee posture. | EXPLICITLY UNIMPLEMENTED | TBD_MODULE | COMMERCIAL | documentation lint rule | lint/trace_ix_clm_03.md |  |
| TRACE-X-SHUT-01 | X-SHUT-01 | Phase X Shutdown Semantics | Shutdown stops inputs and workflows; it does not revise, erase, or soften records. | EXPLICITLY UNIMPLEMENTED | TBD_COMPONENT | EXIT | integration test | tests/test_trace_x_shut_01.py |  |
| TRACE-X-SURV-01 | X-SURV-01 | Phase X Data Survivorship Map | Persistence refers to existence only; usability/accessibility is not guaranteed. | EXPLICITLY UNIMPLEMENTED | TBD_MODULE | EXIT | documentation lint rule | lint/trace_x_surv_01.md |  |
| TRACE-X-IRREV-01 | X-IRREV-01 | Phase X Irreversibility Register | Irreversible actions remain irreversible regardless of shutdown. | EXPLICITLY UNIMPLEMENTED | TBD_COMPONENT | EXIT | integration test | tests/test_trace_x_irrev_01.py |  |
| TRACE-X-DISC-01 | X-DISC-01 | Phase X Exit Disclosure Statement | Exit disclosures must deny closure, safety, correction, or responsibility transfer. | EXPLICITLY UNIMPLEMENTED | TBD_UI_SURFACE | EXIT | documentation lint rule | lint/trace_x_disc_01.md |  |

---

## RESOLVED — ABSENCE Constraints

| Constraint ID | Source (Artifact -> Section) | Constraint Text (Verbatim-Aligned) | Status | No Implementation Required | Do Not Implement |
| --- | --- | --- | --- | --- | --- |
| VI-OP-02 | Phase VI Loop 1 -> Failure Modes | Recorded state may diverge from reality; the system must not assert correspondence to reality. | RESOLVED -- ABSENCE | NO_IMPLEMENTATION_REQUIRED | DO_NOT_IMPLEMENT |
| VI-OP-05 | Phase VI Loop 2 -> Refusal Semantics | Refusal does not imply fault, blame, or correctness. | RESOLVED -- ABSENCE | NO_IMPLEMENTATION_REQUIRED | DO_NOT_IMPLEMENT |
| VII-NG-01 | Phase VII Loop 2 -> Decision Statement | The system asserts no guarantees. | RESOLVED -- ABSENCE (NO IMPLEMENTATION REQUIRED) | NO_IMPLEMENTATION_REQUIRED | DO_NOT_IMPLEMENT |
| VIII-NVIS-ALL | Phase VIII Loops 1-3 | For non-surfaced patterns, the system does not surface visibility due to epistemic limits. | RESOLVED -- ABSENCE | NO_IMPLEMENTATION_REQUIRED | DO_NOT_IMPLEMENT |

---

STOP.
