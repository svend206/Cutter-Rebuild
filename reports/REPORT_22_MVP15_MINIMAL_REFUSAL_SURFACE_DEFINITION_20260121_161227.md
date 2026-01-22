---
doc_id: report_mvp15_minimal_refusal_surface_definition_20260121_161227
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

# REPORT 22 — MVP-15 MINIMAL REFUSAL SURFACE DEFINITION

## Automated Harm / Blame Computation (Concrete)

- Any query that scores, grades, ranks, or labels individual actors/operators by performance or blame.
- Any query that produces leaderboards or “top/worst” operator lists from operational exhaust.
- Any query that assigns normative judgment (good/bad, acceptable/unacceptable) to individual performance.

## Refusal Surface (Query Types / Endpoints)

- Explicit attempts to request blame/score/rank views through a bound query identifier.
- Minimal refusal surface is defined as a fixed set of prohibited `query_ref` values representing blame computation.

## Required Refusal Behavior

- Return an explicit refusal response (no result computation).
- Include a refusal reason category that is non-normative and non-moralizing.
- Emit an auditable refusal event containing actor, query identifier, and timestamp.

## Explicit Non-Goals

- No heuristics
- No partial answers
- No “safe summaries”
- No disguised scoring
