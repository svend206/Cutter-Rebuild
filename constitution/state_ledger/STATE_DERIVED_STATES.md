---
doc_id: state_derived_states
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
tags: [state_ledger, derived_states]
---

# State Ledger — Derived States

## Purpose
This document defines derived states that may be observed within State Ledger.
Derived states are not judgments, diagnoses, or alerts.
They are **structural conditions** that emerge from the persistence, repetition, or interaction of declared states over time.

They exist to make epistemic failure *detectable* without interpretation.

---

## Principles Governing Derived States
All derived states must satisfy the following:
1. They arise only from recorded declarations and time
2. They are mechanically detectable
3. They do not imply severity, causality, or correctness
4. They do not prescribe action
5. They do not depend on external benchmarks

Any state that violates these principles is excluded.

---

## DS-1: Persistent Continuity
**Condition**  
An entity has 2 or more explicit reaffirmations since the most recent reclassification.

**Detection Basis**
- Explicit `declaration_kind = 'REAFFIRMATION'`
- Count of reaffirmations since most recent `RECLASSIFICATION`
- Current run broken by any `RECLASSIFICATION`
- Threshold: 2+ reaffirmations (single reaffirmation not shown)

**Mechanical Requirements**
- Requires explicit `declaration_kind` field (REAFFIRMATION | RECLASSIFICATION)
- No inference from state_text or classification changes
- Caller must declare continuity vs change explicitly

**Meaning**  
The organization has explicitly reaffirmed continuity for this entity via 2+ reaffirmation declarations since last reclassification.

No claim is made about whether this choice is appropriate.

---

## DS-2: Unowned Recognition
**Condition**  
An entity lacks a valid recognition owner for a reporting cycle.

**Detection Basis**
- Absence of assigned recognition owner
- Recognition owner lacks authority

**Meaning**  
Recognition responsibility is undefined.
Epistemic failure is present by definition.

---

## DS-3: Reclassification Without Resolution
**Condition**  
An entity has been reclassified multiple times without entering a stable classification.

**Detection Basis**
- Sequence of reclassifications
- Lack of sustained reaffirmation

**Meaning**  
Reality is being acknowledged as unstable.
No inference is made about cause or consequence.

---

## DS-4: Continuity Under Degradation
**Condition**  
An entity classified as degrading has been reaffirmed without reclassification.

**Detection Basis**
- Classification label
- Consecutive reaffirmations

**Meaning**  
The organization has explicitly accepted continued operation under declared degradation.
No claim is made about recoverability.

---

## DS-5: Deferred Recognition
**Condition**  
An entity's recognition owner fails to reaffirm or reclassify within the expected cadence.

**Detection Basis**
- Missed reaffirmation
- Elapsed time beyond cadence

**Meaning**  
Recognition has been deferred rather than denied.
Silence has occurred where declaration was required.

---

## DS-6: Recognition Concentration
**Condition**  
A single individual holds recognition ownership across multiple critical entities.

**Detection Basis**
- Owner-to-entity mapping

**Meaning**  
Epistemic load is concentrated.
No assessment is made regarding suitability.

---

## DS-7: Continuity Across Authority Change
**Condition**  
An entity's state persists unchanged across changes in leadership or ownership.

**Detection Basis**
- State continuity
- Authority transition markers

**Meaning**  
Prior recognition has been inherited rather than re-examined.
No claim is made about correctness.

---

## Excluded Conditions
The following are explicitly not derived states:
- performance thresholds
- variance limits
- financial ratios
- risk scores
- health indicators
- forecasts
- alerts

Such constructs require interpretation and are outside scope.

---

## Canonical Boundary
Derived states:
- surface structure
- expose continuity
- reveal absence of recognition

They do not:
- explain why
- indicate urgency
- suggest remediation

They exist solely to prevent epistemic failure from remaining invisible.

---

## Closing Statement
Derived states do not add intelligence.
They remove invisibility.

They ensure that persistence, silence, and continuity cannot masquerade as neutrality.
