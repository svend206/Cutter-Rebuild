---
doc_id: state_domain_neutrality
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
tags: [state_ledger, domain_neutrality]
---

# State Ledger — Domain Neutrality

Rules:
- State Ledger content must be industry-agnostic.
- State Ledger must not contain Ops-domain nouns or shop-specific references (e.g., “machine shop”, “machining”, “inspection”, “packing”, “quote”, “CNC”).
- State Ledger declarations may reference Cutter evidence refs, but must not embed Ops domain meaning in `state_text` as nouns.
- If a domain-specific anchor is required, it must live in Ops/Cutter (or via an opaque identifier), never as domain language in State.
