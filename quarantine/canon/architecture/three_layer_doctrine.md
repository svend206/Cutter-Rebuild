---
doc_id: quarantine_three_layer_doctrine
doc_type: context
status: quarantined
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [quarantine]
---

Source: Cutter Layers/canon/architecture/three_layer_doctrine.md

# Three-Layer Architectural Doctrine

**Status:** CANONICAL - Non-Negotiable  
**Date:** January 12, 2026  
**Authority:** Constitutional - These principles govern all implementation  
**Related:** `Docs/_archive/Constitution/Cutter — Canon.md` (formal constraints)

---

## Purpose

This document defines the architectural principles governing the three-layer separation in Cutter. These principles MUST NOT be violated during implementation.

**Constitutional Grounding:** 
- C1-C8 (Canon) define *what* cannot be done
- This document defines *why* the layers must remain separate

---

## Three-Layer Architecture (Do Not Collapse)

- **Ops Layer:** performs work, optimizes workflow, emits exhaust
- **Cutter Ledger:** preserves demonstrated operational reality over time
- **State Ledger:** records explicit human recognition; silence is meaningful

**Core Insight:**

State is sufficient for truth.  
Cutter is required for honesty under pressure.  
Ops is required for livability.

---

## State Ledger Core Insight

State Ledger does not track problems.  
It tracks whether someone with authority has explicitly said what is true, recently enough.

**The unit of record is:**
- a domain of responsibility
- a present-tense statement
- a named authority
- a moment in time

---

## How Topics Enter State Ledger

Topics do not emerge from signals.  
They are pre-declared domains where silence is dangerous.

**Entity creation = declaration that silence is no longer acceptable.**

---

## First Declaration Rule

Creating an entity does not create a state.  
The first explicit declaration creates the initial state.

From then on:
- reaffirmation
- reclassification
- or silence

all become meaningful.

---

## Cutter Ledger Purpose

Cutter Ledger preserves reality so it cannot be forgotten, normalized, or rewritten.  
It never asks for recognition.  
It never infers importance.

---

## UX Boundaries

- **State Ledger UX** = ceremonial, heavy, explicit
- **Cutter Ledger UX** = witness surface, raw, uncomfortable
- **Ops UX** = efficient, helpful, flow-oriented

---

## Canonical UX Test

**"Does this make it easier for the person who carries consequences to unknowingly outrun reality?"**

If yes, it is invalid.

---

## Execution Priority (Current)

Finish Ops → Cutter exhaust before building State Ledger UX.  
State ceremony without preserved reality becomes hollow.

---

## Implementation Guidance

### Layer Boundary Enforcement

**NEVER:**
- Let Ops directly write to State Ledger (only State `boundary.py`)
- Let Cutter Ledger infer importance or priority (outcome agnostic)
- Let State Ledger auto-generate declarations from Cutter events

**ALWAYS:**
- Emit Cutter events for operational exhaust (via `cutter_ledger/boundary.py`)
- Require explicit human recognition for State declarations (via `state_ledger/boundary.py`)
- Keep UX distinct per layer (ceremonial vs. witness vs. flow)

### Test for Violations

1. **Collapse Test:** Could this layer work without the other? (Must be NO for any pairing)
2. **Inference Test:** Does this layer make judgments about another layer's data? (Must be NO)
3. **UX Test:** Does this make it easier to unknowingly outrun reality? (Must be NO)

---

## Cross-References

- **Implementation Constraints:** `.cursorrules`
- **Constitutional Constraints:** `Docs/_archive/Constitution/Cutter — Canon.md`
- **Architecture Details:** `Docs/technical_spec.md`
- **Vision/Mission:** `Docs/project_charter.md` Section 1
