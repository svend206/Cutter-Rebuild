---
doc_id: quarantine_architect_context_pack
doc_type: context
status: quarantined
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [quarantine]
---

Source: Cutter Layers/canon/context/ARCHITECT_CONTEXT_PACK.md

---
doc_id: architect_context_pack
doc_type: context
status: active
version: 1.0
date: 2026-01-16
owner: Erik
authoring_agent: chatgpt
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [architect, context]
---

# Architect Context Pack

## Safe Start (Required Inputs)
- Before execution work: run audit gate; if it triggers, run the audit prompt.
- If identifier neutrality requirements are in scope: requires repo search/confirmation before proceeding.
- If new identifier namespaces are needed: requires repo search/confirmation before proceeding.
- Execution status is authoritative only in `# STATE.md`.

## Governance Gates
- Conformance audit doc: `canon/engineering/conformance_audit.md`
- Audit gate script: `scripts/audit_gate.py`
- Standard test command: `python -m unittest discover -s tests -p "test_*.py" -q`
- Baseline audit tag: `audit-20260117`

## 1) Prime Directive and Layer Separation (authoritative quotes/paraphrase)
- Ops Layer performs work and emits exhaust; Cutter Ledger preserves demonstrated operational reality; State Ledger records explicit human recognition. [file:canon/architecture/three_layer_doctrine.md L20-L24]
- Do not collapse layers; Ops must not directly write to State Ledger; Cutter must not infer importance; State must not auto-generate declarations from Cutter events. [file:canon/architecture/three_layer_doctrine.md L105-L113]
- Cutter Ledger prime directive: preserve sustained operational reality so it cannot remain epistemically invisible. [file:canon/constitution/cutter_ledger/Cutter Ledger - Canon.md L65-L71]
- State Ledger records recognition only; it does not record plans, actions, explanations, or outcomes. [file:canon/constitution/state_ledger/# State Ledger — Canon.md L94-L101]
- Recognition must be explicit with a named authority, timestamp, and scope; no automatic propagation from Cutter to State. [file:canon/constitution/cutter_ledger/# Cutter Ledger ↔ State Ledger — Boundar.md L31-L65]

## 2) State Ledger Constraints (industry-agnostic rules)
- Domain nouns forbidden in State Ledger (e.g., "machine shop", "machining"). [file:canon/constitution/principles/non_collapsing_and_domain_neutrality.md L28-L29]
- Identifiers required to be industry-neutral: requires repo search/confirmation before proceeding.
- State Ledger must not interpret, score, or optimize recognition; it refuses severity encoding, action coupling, optimization pressure, and comfort. [file:canon/constitution/state_ledger/# State Ledger — Canon.md L104-L129] [file:canon/constitution/state_ledger/# State Ledger — System Refusals.md L79-L123]
- State Ledger must not auto-generate or auto-populate declarations; recognition requires explicit human declaration. [file:state_ledger/boundary.py L190-L213]
- State Ledger may reference Cutter Ledger records; no automatic propagation from Cutter to State. [file:canon/constitution/cutter_ledger/# Cutter Ledger ↔ State Ledger — Boundar.md L31-L39]
- State Ledger must not summarize or explain Cutter Ledger data. [file:canon/constitution/cutter_ledger/# Cutter Ledger ↔ State Ledger — Boundar.md L51-L55]

## 3) Cutter Ledger Constraints (epistemic boundaries)
- Cutter Ledger stores operational exhaust: `event_type`, `subject_ref`, `event_data`, timestamps, and provenance. [file:migrations/11_phase4d_subject_ref.py L78-L86] [file:cutter_ledger/boundary.py L153-L157]
- Cutter Ledger is append-only; no update/delete/overwrite. [file:canon/constitution/cutter_ledger/# Cutter Ledger — System Refusals.md L26-L28]
- Cutter Ledger refuses interpretation, ranking, scoring, prioritization, and judgment. [file:canon/constitution/cutter_ledger/# Cutter Ledger — System Refusals.md L34-L55]
- Cutter Ledger must remain industry-agnostic; it must not encode domain-specific concepts or industry-named fields. [file:canon/constitution/cutter_ledger/Cutter Ledger - Canon.md L96-L104]
- Event types must be descriptive and non-evaluative. [file:cutter_ledger/boundary.py L81-L116]

## 4) Query/Help Surface Rules
- Cutter Ledger UX must show raw events and timestamps; must not rank, score, color, or suggest action. [file:canon/constitution/UX/# LEDGER UX CONSTITUTION (NON-NEGOTIABLE).md L26-L43]
- State Ledger derived states must be mechanically detectable, not imply severity or causality, and prescribe no action. [file:canon/constitution/state_ledger/# State Ledger — Derived States.md L14-L23]
- Ledger Query CLI is read-only and outputs raw data only; no summaries, recommendations, alerts, health checks, or scoring. [file:scripts/ledger_query_cli.py L3-L11]
- State Ledger query functions explicitly forbid inference, scoring, and prioritization in outputs. [file:state_ledger/queries.py L61-L67]
- Cutter Ledger excludes aggregation that collapses history (no smoothing, no snapshots). [file:canon/constitution/cutter_ledger/# Cutter Ledger — Exclusions.md L72-L83]

## 5) Identifier Namespaces (authoritative)
- State `entity_ref` format: `{org_ref}/entity:{type}:{local_id}` with examples. [file:canon/constitution/identifier_conventions.md L63-L78]
- State `scope_ref` format: `{org_ref}/scope:{context}` with examples. [file:canon/constitution/identifier_conventions.md L89-L102]
- State `actor_ref` format: `{org_ref}/actor:{local_id}` (used by declarations/ownership). [file:canon/constitution/identifier_conventions.md L38-L56]
- Cutter `subject_ref` examples: `"quote:{id}"`, `"job:456"`, `"unknown"`. [file:cutter_ledger/boundary.py L92-L95]
- Cutter `event_type` rules: descriptive only; must not contain evaluative language. [file:cutter_ledger/boundary.py L81-L116]
- Cutter `event_type` vocabulary (quote lifecycle) and `subject_ref` format `quote:{id}`. [file:canon/decision_log/quote_lifecycle_event_vocabulary.md L18-L49]
- Cutter `event_data` conventions: only directly provided data, no inferred fields. [file:canon/decision_log/quote_lifecycle_event_vocabulary.md L171-L189]
- If other identifier namespaces are required (beyond the above): requires repo search/confirmation before proceeding.

## 6) Implemented Reality Snapshot (facts)
- Cutter schema (latest migration): `cutter__events` columns and indexes. [file:migrations/11_phase4d_subject_ref.py L78-L136]
- State schema (latest migrations): `state__declarations` columns (including `declaration_kind` and `classification`) and indexes. [file:migrations/12_phase5_state_ledger.py L105-L135] [file:migrations/13_phase5e_declaration_kind.py L118-L133] [file:migrations/14_add_classification_column.py L72-L75]
- State schema (support tables): `state__entities`, `state__recognition_owners` (creation shown in migration 12). [file:migrations/12_phase5_state_ledger.py L57-L92]
- Boundary write entry points:
  - `emit_cutter_event()` in `cutter_ledger/boundary.py`. [file:cutter_ledger/boundary.py L68-L79]
  - `emit_state_declaration()` in `state_ledger/boundary.py`. [file:state_ledger/boundary.py L190-L203]
- Read-only query surfaces:
  - CLI: `scripts/ledger_query_cli.py` (usage in docstring; read-only guard). [file:scripts/ledger_query_cli.py L3-L23]
  - State query helpers: `state_ledger/queries.py` (list_entities, query_persistent_continuity, get_latest_declarations). [file:state_ledger/queries.py L26-L117]
  - Cutter query script: `query_override_events.py` (read-only ledger queries). [file:query_override_events.py L1-L12]

## 7) Known Conflicts / Ambiguities
- State Ledger Canon says "No Interpretation" but also states "interpretation is embedded in classification" (potential conflict). [file:canon/constitution/state_ledger/# State Ledger — Canon.md L104-L114] [file:canon/constitution/state_ledger/# State Ledger — Canon.md L151-L156]
- State Ledger derived states include classification-based conditions (e.g., "degrading") while System Refusals reject severity encoding labels (potential ambiguity). [file:canon/constitution/state_ledger/# State Ledger — Derived States.md L87-L96] [file:canon/constitution/state_ledger/# State Ledger — System Refusals.md L79-L88]
- Cutter Ledger canon forbids domain-specific concepts, but quote event vocabulary includes domain-specific fields (material, quantity) in `event_data` (potential conflict). [file:canon/constitution/cutter_ledger/Cutter Ledger - Canon.md L96-L104] [file:canon/decision_log/quote_lifecycle_event_vocabulary.md L26-L36]
- Migration 14 checks for trigger names `block_state_declarations_*` while migrations 12/13 create `prevent_declaration_*` (trigger name mismatch). [file:migrations/14_add_classification_column.py L103-L106] [file:migrations/12_phase5_state_ledger.py L140-L154]
