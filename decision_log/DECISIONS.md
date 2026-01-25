---
doc_id: decision_log
doc_type: decision_log
status: active
version: 2.3
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: [archive/DECISION_LOG.md]
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [decision_log, governance]
---

# Decision Log

Append-only log of binding decisions.

## Entry Format (Required)
Each entry must include:
- Date (YYYY-MM-DD)
- Decision (one sentence)
- Scope (what is affected)
- Authority (who made it)
- Rationale (one sentence)
- Supersedes (optional, list of prior decisions)

## Entries
- Date: 2026-01-26
  Decision: Added Constitutional Amendment v5 to expand Phase X exit artifacts.
  Scope: boot/PROJECT_PHASE_CONSTITUTION.md
  Authority: Erik
  Rationale: Make shutdown, survivorship, and irreversibility constraints explicit and auditable.
  Supersedes: none
- Date: 2026-01-26
  Decision: Added Constitutional Amendment v4 to insert a dedicated Guarantees phase and renumber post-reliance phases.
  Scope: boot/PROJECT_PHASE_CONSTITUTION.md
  Authority: Erik
  Rationale: Make guarantees explicit, auditable, and refusal-bound with clear phase sequencing.
  Supersedes: none
- Date: 2026-01-21
  Decision: Clarified Guild execution-variance language to avoid implicit scoring or blame.
  Scope: constitution/guild/GUILD_ALLOWED_QUESTIONS_AND_EXHAUST_MAP.md
  Authority: Erik
  Rationale: Prevent execution-risk phrasing from being read as shop evaluation or blame.
  Supersedes: none
- Date: 2026-01-21
  Decision: Clarified constitutional prohibitions on blocking execution for settlement or required explanations, and on implicit scoring or performance evaluation.
  Scope: constitution/ops_layer/OPS_CANON.md; constitution/CORE_INTERPRETATION_BOUNDARY.md
  Authority: Erik
  Rationale: Remove ambiguity that could allow execution gating or evaluative scoring.
  Supersedes: none
- Date: 2026-01-21
  Decision: Codified seven constitutional invariants covering reconciliation scope, execution continuity, capture boundaries, harm/blame refusal, mode separation, stability over freshness in judgment, and attention authorization.
  Scope: constitution/CORE_QUERY_LAYER_RULES.md; constitution/CORE_INTERPRETATION_BOUNDARY.md; constitution/ops_layer/OPS_CANON.md; constitution/CORE_LEDGER_UX.md; constitution/CORE_UX_LANGUAGE_BOUNDARY.md
  Authority: Erik
  Rationale: Make binding invariants explicit at the constitutional layer.
  Supersedes: none
- Date: 2026-01-19
  Decision: Recorded MVP audit via repository audit tag.
  Scope: governance audit record
  Authority: Erik
  Rationale: Preserve a durable, traceable audit milestone.
  Supersedes: none
- Date: 2026-01-18
  Decision: Made offline-first operation and SQLite WAL persistence constitutional constraints.
  Scope: core system persistence and dependencies
  Authority: Erik
  Rationale: Preserve local sovereignty and durability as non-negotiable foundations.
  Supersedes: none
- Date: 2026-01-18
  Decision: Added constitutional UX index to centralize UX boundary references.
  Scope: UX constitution structure
  Authority: Erik
  Rationale: Improve discoverability without adding new UX doctrine.
  Supersedes: none
- Date: 2026-01-18
  Decision: Forbid credits/incentives/contribution scoring outside the Guild surface.
  Scope: Cutter–Guild boundary, UI/UX surfaces
  Authority: Erik
  Rationale: Prevent Guild economics from leaking into Ops/Cutter/State behavior.
  Supersedes: none
- Date: 2026-01-18
  Decision: Established decision log at `decision_log/DECISIONS.md` and archived the prior root log.
  Scope: governance documentation
  Authority: Erik
  Rationale: Preserve binding decisions in a single authoritative log.
  Supersedes: none
- Date: 2026-01-18
  Decision: Added document governance discipline rules (supersession protocol, decision-log requirement for constitutional changes, location conventions).
  Scope: document governance constitution
  Authority: Erik
  Rationale: Prevent drift and ensure atomic authority updates.
  Supersedes: none
- Date: 2026-01-18
  Decision: Standardized decision log entry format for consistency and auditability.
  Scope: decision log
  Authority: Erik
  Rationale: Keep decisions readable and structured.
  Supersedes: none
- Date: 2026-01-18
  Decision: Added governance discipline rules for spec reuse, atomic authority updates, and scan-ability.
  Scope: document governance constitution
  Authority: Erik
  Rationale: Keep the repo lean and easy to navigate for humans and agents.
  Supersedes: none
- Date: 2026-01-18
  Decision: Allowed context documents to live in `architecture/` for descriptive system memory.
  Scope: document governance constitution
  Authority: Erik
  Rationale: Enable architecture memory without granting authority.
  Supersedes: none
- Date: 2026-01-18
  Decision: Archived the rebuild plan after completion and moved it to `archive/`.
  Scope: bootstrap pack, directory registry
  Authority: Erik
  Rationale: Preserve the plan without keeping it authoritative.
  Supersedes: none
- Date: 2026-01-18
  Decision: Added a promotion checklist for evaluating old-repo artifacts before import.
  Scope: architecture context, promotion workflow
  Authority: Erik
  Rationale: Prevent redundancy and authority drift during migration.
  Supersedes: none
- Date: 2026-01-18
  Decision: Added a quarantine area for uncertain documents, treated as context-only.
  Scope: document governance constitution, directory registry
  Authority: Erik
  Rationale: Defer unclear artifacts without granting authority.
  Supersedes: none
