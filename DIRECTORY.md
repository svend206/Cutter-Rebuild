---
doc_id: directory
doc_type: spec
status: active
version: 2.0
date: 2026-01-18
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
- `constitution/CORE_INTERPRETATION_BOUNDARY.md`
- `constitution/CORE_NON_COLLAPSING.md`
- `constitution/CORE_QUERY_LAYER_RULES.md`
- `constitution/CORE_UX_LANGUAGE_BOUNDARY.md`
- `constitution/CORE_LEDGER_UX.md`
- `constitution/CORE_LEDGER_BOUNDARY.md`
- `constitution/CORE_IDENTIFIER_CONVENTIONS.md`
- `constitution/CORE_GUILD_BOUNDARY.md`

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
- `bootstrap/BOOTSTRAP_INDEX.md`
- `bootstrap/CONSTITUTION_INDEX.md`
- `bootstrap/CONSTITUTION_MISREAD_TEST.md`
- `integrator/INTEGRATOR_HOME.md`
- `inbox/INBOX.md`
- `obligations/OBLIGATIONS.md`

---

## D. Context (Non-Authoritative)
- `context/STATE_LEDGER_MANIFESTO.md`
- `context/CONSTITUTION_RULE_MAP.md`
- `architecture/ARCHITECTURE_INDEX.md`
- `architecture/NAVIGATION_INDEX.md`
- `architecture/PROMOTION_CHECKLIST.md`
- `packs/ARCHITECT.md`
- `packs/BUILDER.md`
- `packs/UI_UX.md`
- `packs/OPS.md`
- `packs/CUTTER.md`
- `packs/STATE.md`
- `packs/GUILD.md`
- `quarantine/QUARANTINE_INDEX.md`
- `quarantine/CLASSIFICATION_LOG.md`
- `quarantine/REMAINDER_MANIFEST.md`

---

## E. Archive (Non-Authoritative)
- `archive/DECISION_LOG.md`
- `archive/CLEAN_REBUILD_EXECUTION_PLAN.md`

---

## Update Protocol
- Any new authoritative document must be added here.
- Any move, rename, or supersession must be reflected here.
- If a document is not listed above, it has **no authority**.
