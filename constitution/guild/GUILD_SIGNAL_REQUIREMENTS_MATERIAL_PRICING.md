---
doc_id: guild_signal_requirements_material_pricing
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
tags: [guild, signals, material_pricing]
---

# Guild Signal Requirements — Material Pricing (Authoritative)

## Purpose
Define the minimum raw exhaust required for shop-side material pricing intelligence.

## Required Signals
- MATERIAL_QUOTED_PRICE
- MATERIAL_PURCHASED_PRICE
- MATERIAL_QUANTITY_BREAK
- MATERIAL_TRANSACTION_CONTEXT
- MATERIAL_SUPPLIER_CATEGORY

All signals are raw, uninterpreted, and shop-generated.

## Aggregation Rules
- distributions only
- no “fair price”
- no recommendations

Status: LOCKED
