---
doc_id: directory
doc_type: spec
status: active
version: 6.2
date: 2026-01-22
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [governance, registry]
---

# DIRECTORY

## Purpose
Single source of truth for **authoritative documents** and load order.

Authority lives in files, not in chat.

---

## Authority Hierarchy
1. Constitution
2. Decision Log
3. Specs
4. Context (non-authoritative)
5. Archive

---

## A. Constitution (Authoritative)

### Core
- `constitution/CONSTITUTION_AUTHORITY.md`
- `constitution/CORE_DOC_GOVERNANCE.md`
- `constitution/CORE_LOCAL_FIRST.md`
- `constitution/CORE_INTERPRETATION_BOUNDARY.md`
- `constitution/CORE_NON_COLLAPSING.md`
- `constitution/CORE_QUERY_LAYER_RULES.md`
- `constitution/CORE_UX_LANGUAGE_BOUNDARY.md`
- `constitution/CORE_LEDGER_UX.md`
- `constitution/CORE_LEDGER_BOUNDARY.md`
- `constitution/CORE_IDENTIFIER_CONVENTIONS.md`
- `constitution/CORE_GUILD_BOUNDARY.md`
- `constitution/ux/UX_INDEX.md`

### Ops Layer
- `constitution/ops_layer/OPS_CANON.md`
- `constitution/ops_layer/OPS_NORMAL.md`
- `constitution/ops_layer/OPS_EXCLUSIONS.md`
- `constitution/ops_layer/OPS_REFUSALS.md`

### Cutter Ledger
- `constitution/cutter_ledger/CUTTER_CANON.md`
- `constitution/cutter_ledger/CUTTER_NORMAL.md`
- `constitution/cutter_ledger/CUTTER_EXCLUSIONS.md`
- `constitution/cutter_ledger/CUTTER_REFUSALS.md`

### State Ledger
- `constitution/state_ledger/STATE_CANON.md`
- `constitution/state_ledger/STATE_NORMAL.md`
- `constitution/state_ledger/STATE_EXCLUSIONS.md`
- `constitution/state_ledger/STATE_REFUSALS.md`
- `constitution/state_ledger/STATE_DERIVED_STATES.md`
- `constitution/state_ledger/STATE_DOMAIN_NEUTRALITY.md`
- `constitution/state_ledger/STATE_NEVER_BECOME.md`

### Guild
- `constitution/guild/GUILD_CONSTITUTION.md`
- `constitution/guild/GUILD_ALLOWED_QUESTIONS_AND_EXHAUST_MAP.md`
- `constitution/guild/GUILD_SIGNAL_REQUIREMENTS_MATERIAL_PRICING.md`
- `constitution/guild/GUILD_SIGNAL_REQUIREMENTS_CAPACITY_LEAD_TIME.md`
- `constitution/guild/GUILD_GENESIS_HASH_SYSTEM_SPEC.md`

---

## B. Decision Log (Authoritative)
- `decision_log/DECISIONS.md`

---

## C. Specs (Authoritative)
- `boot/BOOT_CONTRACT.md`
- `boot/PROJECT_PHASE_CONSTITUTION.md`
- `bootstrap/BOOTSTRAP_INDEX.md`
- `bootstrap/CONSTITUTION_INDEX.md`
- `bootstrap/CONSTITUTION_MISREAD_TEST.md`
- `bootstrap/MVP Capability Definition.md`
- `integrator/INTEGRATOR_HOME.md`
- `inbox/INBOX.md`
- `obligations/OBLIGATIONS.md`
- `planning/Phase_I_work_charter.md`
- `planning/PHASE_II_WORK_CHARTER.md`
- `planning/PHASE_II_RECORD_TYPES_CATALOG.md`
- `planning/PHASE_II_REPRESENTATION_INVARIANTS.md`
- `planning/PHASE_III_WORK_CHARTER.md`
- `planning/PHASE_III_BINDING_MATRIX.md`
- `planning/PHASE_IV_WORK_CHARTER.md`
- `planning/PHASE_IV_EXPOSURE_INVARIANTS.md`
- `planning/PHASE_IV_EXPOSURE_VIEWS_CATALOG.md`
- `planning/PHASE_V_WORK_CHARTER.md`
- `planning/PHASE_VI_WORK_CHARTER.md`
- `planning/PHASE_VI_LOOP_1.md`
- `planning/PHASE_VI_LOOP_1_AUDIT.md`
- `planning/PHASE_VI_LOOP_2.md`
- `planning/PHASE_VII_WORK_CHARTER.md`
- `planning/PROJECT_PHASE_CONSTITUTION_AMENDMENT_AUDIT.md`
- `ux/UX_INDEX.md`
- `ux/ui_surface_rules_and_pages.md`
- `ux/SYSTEM_PAGE_PURPOSE_SPEC.md`
- `ops_layer/mode_seperation.md`

---

## D. Context (Non-Authoritative)
- `context/STATE_LEDGER_MANIFESTO.md`
- `context/CONSTITUTION_RULE_MAP.md`
- `context/MVP_CAPABILITIES_LOCKED.md`
- `context/MVP_V2_REBASELINE_DECLARATION.md`
- `context/MVP_V2_COVERAGE_ASSERTION_TABLE.md`
- `context/UI_REALITY_REPORT.md`
- `context/UI_SUFFICIENCY_MATRIX_FOR_MVP.md`
- `context/PLAN_INPUTS_GAP_MAP.md`
- `context/MVP_VERIFICATION_GAP_ANALYSIS.md`
- `context/UI_Verification_Loop_Checklist.md`
- `context/UI_VERIFICATION_SPEC_MVP-1.md`
- `context/UI_VERIFICATION_SPEC_MVP-12.md`
- `context/UI_VERIFICATION_SPEC_MVP-13.md`
- `context/UI_VERIFICATION_SPEC_MVP-14.md`
- `context/UI_VERIFICATION_SPEC_MVP-15.md`
- `context/MVP_15_REFUSAL_SURFACE_VERIFICATION.md`
- `context/MVP_LOCK_AT_TAG.md`
- `context/POST_MVP_INTENT.md`
- `context/UNLOCK_MVP.md.template`
- `context/manifesto/CORE_MANIFESTO.md`
- `context/manifesto/# Cannot Outsource Risk.md`
- `context/manifesto/think_different.md`
- `context/manifesto/Why Cutter.md`
- `architecture/ARCHITECTURE_INDEX.md`
- `architecture/SCHEMA_REFERENCE.md`
- `architecture/NAVIGATION_INDEX.md`
- `architecture/NAVIGATION_DRIFT_REPORT.md`
- `architecture/PROMOTION_CHECKLIST.md`
- `reports/REPORT_1_CURRENT_CAPABILITY_INVENTORY.md`
- `reports/REPORT_2_SYSTEM_SURFACES_AND_ENTRYPOINTS.md`
- `reports/REPORT_3_DATA_AND_SCHEMA_FACTS.md`
- `reports/REPORT_4_TEST_AND_RUNTIME_STATUS.md`
- `reports/REPORT_5_GOVERNANCE_INTEGRITY_CHECK.md`
- `reports/REPORT_6_DOC_INTEGRITY_POST_REBASELINE_20260121_141758.md`
- `reports/REPORT_7_GATE_TEST_POST_REBASELINE_20260121_141758.md`
- `reports/REPORT_8_READY_TO_IMPLEMENT_READOUT_20260121_141758.md`
- `reports/REPORT_9_AUDIT_GATE_REMEDIATION_PLAN_20260121_142350.md`
- `reports/REPORT_10_TEST_REMEDIATION_LOG_20260121_142350.md`
- `reports/REPORT_11_REPO_GREEN_STATUS_20260121_144518.md`
- `reports/REPORT_12_OPS_MODE_DEFAULT_COMPAT_CHECK_20260121_145011.md`
- `reports/REPORT_14_MVP12_MINIMAL_DELTA_DEFINITION_20260121_152753.md`
- `reports/REPORT_15_MVP12_VERIFICATION_EVIDENCE_20260121_153518.md`
- `reports/REPORT_16_MVP13_MINIMAL_DELTA_DEFINITION_20260121_154129.md`
- `reports/REPORT_17_MVP13_VERIFICATION_EVIDENCE_20260121_154640.md`
- `reports/REPORT_18_MVP13_LOOP1_VERIFICATION_CHECK_20260121_155157.md`
- `reports/REPORT_19_MVP14_MINIMAL_DELTA_DEFINITION_20260121_155251.md`
- `reports/REPORT_20_MVP14_VERIFICATION_EVIDENCE_20260121_155448.md`
- `reports/REPORT_21_MVP12_13_14_PROOF_TIGHTENING_EVIDENCE_20260121_160351.md`
- `reports/REPORT_22_MVP15_MINIMAL_REFUSAL_SURFACE_DEFINITION_20260121_161227.md`
- `reports/REPORT_23_MVP15_VERIFICATION_EVIDENCE_20260121_161456.md`
- `reports/REPORT_24_MVP15_HARDENED_REFUSAL_BOUNDARY_DEFINITION_20260121_161924.md`
- `reports/REPORT_25_MVP15_HARDENING_VERIFICATION_EVIDENCE_20260121_162142.md`
- `reports/REPORT_26_MVP15_HARDENED_CHECKPOINT_COMMIT_20260121_162511.md`
- `reports/REPORT_27_TEST_ARTIFACT_HYGIENE_20260121_162931.md`
- `reports/REPORT_28_UI_HARNESS_MINIMAL_DELTA_DEFINITION_20260122_060018.md`
- `reports/REPORT_29_UI_HARNESS_VERIFICATION_EVIDENCE_20260122_060332.md`
- `reports/REPORT_30_UI_HARNESS_CHECKPOINT_COMMIT_20260122_062122.md`
- `reports/REPORT_32_UI_HARNESS_ASSIGN_OWNER_EVIDENCE_20260121_120500.md`
- `reports/REPORT_33_AUDIT_OVERRIDE_CLEARED_20260122_170632.md`
- `reports/REPORT_34_AUDIT_TAG_ALIGNMENT_20260122_172935.md`
- `reports/REPORT_35_PHASE_I_ADVERSARIAL_TESTS_20260123_113450.md`
- `reports/REPORT_36_PHASE_I_CLOSURE_AUDIT_20260123_114810.md`
- `reports/REPORT_37_PHASE_II_ADVERSARIAL_EXIT_AUDIT_20260123_150000.md`
- `reports/REPORT_38_PHASE_II_CLOSURE_AUDIT_20260123_151000.md`
- `reports/REPORT_39_PHASE_III_ADVERSARIAL_AUDIT_20260123_152500.md`
- `reports/REPORT_40_PHASE_IV_ADVERSARIAL_EXIT_AUDIT_20260123_160000.md`
- `reports/AUDIT_PHASE_V_RELIANCE.md`
- `scripts/README.md`
- `tests/README.md`
- `packs/ARCHITECT.md`
- `packs/BUILDER.md`
- `packs/UI_UX.md`
- `packs/OPS.md`
- `packs/CUTTER.md`
- `packs/STATE.md`
- `packs/GUILD.md`

---

## E. Archive (Non-Authoritative)
- `archive/DECISION_LOG.md`
- `archive/CLEAN_REBUILD_EXECUTION_PLAN.md`
- `archive/MVP Gap Analysis.md`
- `archive/MVP Plan.md`
- `archive/mvp-to-mvp-plan_c1dc08dc.plan.md`
- `archive/Docs/_archive/Constitution/Cutter — Canon.md`
- `archive/Docs/_archive/Constitution/Cutter — Exclusions.md`
- `archive/Docs/_archive/Constitution/Cutter — Normal Operating Conditions.md`
- `archive/Docs/_archive/Constitution/Cutter — System Refusals.md`
- `archive/Docs/_archive/Constitution/Cutter ↔ State Vault — Boundary & Symmet.md`
- `archive/Docs/_archive/Constitution/Open Questions`
- `archive/Docs/_archive/Constitution/Open Questions.md`
- `archive/Docs/_archive/implementation_logs/GENESIS_HASH_PATTERN_MATCHING_COMPLETE.md`
- `archive/Docs/_archive/implementation_logs/PHASE_5_DOCUMENTATION_UPDATE.md`
- `archive/Docs/_archive/implementation_logs/README.md`
- `archive/Docs/_archive/refactoring_process/_REFACTOR_COMPLETE_SUMMARY.md`
- `archive/Docs/_archive/refactoring_process/_REFACTOR_FINAL_REPORT.md`
- `archive/Docs/_archive/refactoring_process/_REVIEW_WITH_GEMINI.md`
- `archive/Docs/_archive/refactoring_process/DOC_REFACTOR_PLAN.md`
- `archive/Docs/_archive/refactoring_process/README.md`

---

## Update Protocol
- Any new authoritative document must be added here.
- Any move, rename, or supersession must be reflected here.
- If a document is not listed above, it has **no authority**.
