---
doc_id: ui_verification_spec_mvp_15
doc_type: context
status: active
version: 1.0
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [ui, verification, mvp, context]
---

# UI Verification Spec — MVP-15

## MVP Capability

**MVP-15 — The system explicitly refuses automated harm and blame computation**

**Capability**  
The system can explicitly refuse to compute, retain, or present views that automate, scale, or normalize individual blame, performance scoring, or normative judgment.

**Success condition**  
When such queries or views are attempted, the system responds with an explicit refusal rather than silent omission or deferred implementation.

## How a Human Attempts to Violate the Guarantee

- Attempt to locate any UI surface that computes or presents blame, performance scoring, or normative judgment.  
  Evidence of existing UI surfaces: `context/UI_REALITY_REPORT.md`
- Limitation: The UI reality report does not describe such surfaces, so violation attempts are limited to confirming their absence.

## What the UI Must Show to Observe the Outcome (Minimum)

- The current UI does not expose refusal surfaces for harm or blame computation; therefore, the minimum observable signals for explicit refusal are not present.
  Evidence of UI observability limits: `context/UI_REALITY_REPORT.md`, `context/UI_SUFFICIENCY_MATRIX_FOR_MVP.md`, `context/MVP_15_REFUSAL_SURFACE_VERIFICATION.md`

## Explicit Non-Goals (Forbidden UI Elements)

- Summaries
- Success indicators
- Guidance
- Aggregation
- Inferred status
- Any “helpfulness”
