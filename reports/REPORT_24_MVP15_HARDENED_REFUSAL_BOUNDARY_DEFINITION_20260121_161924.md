---
doc_id: report_mvp15_hardened_refusal_boundary_definition_20260121_161924
doc_type: context
status: active
version: 1.0
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [context/MVP_CAPABILITIES_LOCKED.md, constitution/CORE_INTERPRETATION_BOUNDARY.md, constitution/CORE_QUERY_LAYER_RULES.md, constitution/ops_layer/OPS_REFUSALS.md]
conflicts_with: []
tags: [report, mvp15, refusal, context]
---

# REPORT 24 — MVP-15 HARDENED REFUSAL BOUNDARY DEFINITION

## Query Classification / Taxonomy (Authoritative)

- `allowed`
- `refuse_blame`

## Deterministic Rule

- Any query classified as `refuse_blame` MUST refuse explicitly, regardless of query_ref, phrasing, or payload wording.

## Classification Resolution (Non-Heuristic)

- Classification is resolved by an explicit registry mapping `query_ref` → `query_class`.
- If no mapping exists, refusal is mandatory (fail-closed).

## Required Refusal Behavior

- Explicit refusal response (no computation).
- Refusal category is non-normative and non-moralizing.
- Auditable refusal event includes actor, query_ref, query_class, and timestamp.

## Explicit Non-Goals

- No heuristics
- No ML or inference from text
- No partial answers
- No “safe summaries”
