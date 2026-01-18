---
doc_id: guild_constitution
doc_type: constitution
status: locked
version: 1.1
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - constitution/CORE_GUILD_BOUNDARY.md
conflicts_with: []
tags: [guild, constitution]
---

# The Guild — Constitution (Locked)

## Purpose
The Guild exists to **eliminate information asymmetry between machine shops and their customers and suppliers**.

The Guild explicitly takes the side of **machine shops as a class**.
The Guild does **not** attempt to equalize outcomes among shops, protect shops from one another, or constrain how information is used.

It is a **market intelligence system**, not an operational system and not an epistemic safety system.

---

## Foundational Commitments (Authoritative)
The Guild makes exactly two commitments:
1. **Side-taking**: Guild intelligence is produced *for machine shops only*.  
   Customers and suppliers are not constituents.
2. **Information parity**: Any market information that customers possess (or its functional equivalent) is legitimate for shops to possess.

No other normative commitments are implied.

---

## What the Guild Is
The Guild is:
- a **shop-only market intelligence exchange**
- a system for revealing **real market conditions**, including competitive density and attention
- a layer that may surface **raw, delayed, or real-time intelligence**
- intentionally **non-paternalistic** with respect to how information is used

The Guild may influence behavior via information disclosure but is **never prescriptive**: it does not recommend actions, command pricing, rank shops, or direct "you should charge X."

The Guild answers the question:
> “What information do customers and suppliers already have that I do not?”

---

## What the Guild Is Not
The Guild is not:
- a decision-maker
- a fiduciary
- a regulator
- a fairness engine
- an outcome equalizer

The Guild does **not** attempt to:
- prevent coordination among shops
- suppress competition among shops
- protect slower or smaller shops from faster or larger ones

---

## Relationship to Cutter (Hard Firewall)
See `constitution/CORE_GUILD_BOUNDARY.md`.

---

## Information Discipline
The Guild may surface intelligence that is:
- object-level or class-level
- real-time or historical
- aggregated or raw

**Provided that**:
- the intelligence is available **only to machine shops**
- the intelligence reflects **observed reality**, not prescription
- the intelligence does not fabricate certainty where none exists

The Guild does not filter intelligence to prevent behavioral impact.

---

## Identity & Correlation
The Guild **may**:
- use stable identifiers (including geometry-derived identifiers)
- surface object-level intelligence
- surface real-time competitive signals
- enable coordination effects among shops

Provided that:
- access is restricted to machine shops
- customers and suppliers cannot access the same intelligence

---

## API Access
APIs may be offered provided that:
- access is restricted to shop-side entities or their agents
- customers and suppliers cannot access the same intelligence
- provenance and accuracy are preserved

Redistribution to non-shop entities voids access.

---

## Revision Semantics (Additive-Only)
Guild contributions and aggregates are **additive-only** with provenance preservation:

**Allowed**:
- Post-hoc revisions as new records/versions
- Recomputation of aggregates from revised inputs
- Appending corrected or updated contributions

**Required**:
- Provenance link to prior record(s)
- Prior versions remain reconstructible
- Audit trail of what changed and when

**Forbidden**:
- Deleting prior contributions without trace
- Overwriting aggregates without version preservation
- Destructive updates that erase provenance

**Rationale**: Shops must be able to verify that intelligence reflects actual contributions, not post-hoc manipulation.

---

## Drift Test (Authoritative)
If a reviewer can say:
> “The Guild concealed information that customers already had.”

Then the system has violated this Constitution.

---

## Status
LOCKED — This Constitution supersedes all prior Guild constitutions.
