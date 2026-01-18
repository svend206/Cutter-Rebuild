---
doc_id: guild_genesis_hash_system_spec
doc_type: constitution
status: locked
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [guild, genesis_hash]
---

# Genesis Hash System — Guild Real-Time Part Intelligence (Locked)

## Purpose
Provide shop-only, real-time intelligence about part-level competition.

## Genesis Hash Role (Choice B — Binding)
The genesis hash is a **geometry-derived index key**:
- derived from part volume + sorted dimensions
- non-reversible, stable across shops
- deterministic (same geometry → same hash)

**Allowed use**: Guild-only real-time/near-real-time distributions and counts keyed by genesis_hash.

**Forbidden use**:
- Prediction, prescription, or recommendations
- Surfacing inside Ops workflows, Cutter Ledger UX, or State Ledger UX
- Any implicit guidance or competitive signal leakage into operational surfaces
- Use as basis for "should" or "recommend" logic

**Access constraint**: Requires explicit context switch to Guild product.

## Core Design
- geometry-derived feature vector
- quantized
- HMAC-based genesis hash
- shop-only access

## Guild-Observed Events
The Guild may observe (from exported exhaust) events including:
- PART_VIEWED
- QUOTE_STARTED_FOR_PART
- QUOTE_SUBMITTED_FOR_PART

These are **Guild-observed only**. They do not trigger Ops behaviors and must not appear in Ops/Cutter/State UX.

## Anti-Abuse
- dedup windows
- shop verification
- query gating (must open locally)
- rate limits

## Outputs
- counts only (e.g., "3 shops quoted this hash today")
- distributions (time-bucketed or cumulative)
- no shop identities
- explicit "no observations" states

## UI Surface
Guild-only. Explicit context switch required.

No genesis_hash-derived intelligence may appear in Ops, Cutter Ledger, or State Ledger UX.

---

**Status**: LOCKED — Choice B binding as of 2026-01-13
