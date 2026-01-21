---
doc_id: ui_verification_spec_mvp_1
doc_type: context
status: active
version: 1.0
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [ui, verification, mvp, context]
---

# UI Verification Spec — MVP-1

## MVP Capability

**MVP-1 — Ops can perform work and emit exhaust**

**Capability**
The system can allow a user to perform operational actions while emitting immutable operational exhaust for each action.

**Success condition**
For any permitted operational action, a corresponding exhaust record exists that includes actor identity, timestamp, and action-relevant values, and that record cannot be altered or deleted.

## How a Human Attempts to Violate the Guarantee

- Use the UI to perform an operational action that currently exists (upload a 3D file and calculate a quote, or choose Manual Entry and define a part), then attempt to find any UI-visible exhaust trace of that action.
  Evidence of operational actions and surfaces: `context/UI_REALITY_REPORT.md`

## What the UI Must Show to Observe the Outcome (Minimum)

- The current UI does not expose a ledger or exhaust record view; therefore, the minimum observable UI signals needed to confirm exhaust emission (actor, timestamp, action linkage) are not present.
  Evidence of UI observability limits: `context/UI_REALITY_REPORT.md`, `context/UI_SUFFICIENCY_MATRIX_FOR_MVP.md`

## Explicit Non-Goals (Forbidden UI Elements)

- Summaries
- Success indicators
- Guidance
- Aggregation
- Inferred status
- Any “helpfulness”
