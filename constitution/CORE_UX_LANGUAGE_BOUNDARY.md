---
doc_id: core_ux_language_boundary
doc_type: constitution
status: locked
version: 1.2
date: 2026-01-21
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [ux, language]
---

# UX Language Boundary

## What to capture
Users may speak in their language.  
The system must never think in that language.

Concrete UX rules to capture:
- User terms allowed only as labels or predicates
- Refusals appear only at boundary crossings
- Attention must never be pulled unless explicitly authorized by the user. <!-- Invariant 7 -->

Predicate transparency and instance-first constraints are defined in
`constitution/CORE_QUERY_LAYER_RULES.md`.

## Why
Without this, you’ll either alienate users or violate constitution. This is the needle.

---

## Summary of Amendments
- Added attention authorization rule for UX behavior (Invariant 7).
