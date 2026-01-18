---
doc_id: state_refusals
doc_type: constitution
status: locked
version: 1.1
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [state_ledger, refusals]
---

# State Ledger — System Refusals

## Purpose
This document defines behaviors, requests, and conditions that State Ledger will explicitly refuse.
Refusal is not a failure of the system.
Refusal is the system’s primary mechanism for preserving epistemic integrity.

Any implementation that complies with these refused behaviors is not State Ledger.

---

## Refusal Principle
State Ledger refuses any interaction that would allow recognition to be:
- avoided
- softened
- delayed
- negotiated
- overwritten

The system must remain inhospitable to epistemic compromise.

---

## Canonical Refusals

### R1. Refusal of Implicit Continuity
State Ledger refuses to carry a state forward without explicit reaffirmation.

Silence is not a valid declaration.

---

### R2. Refusal of Default Acknowledgment
State Ledger refuses pre-filled, suggested, or auto-selected state values.
Every declaration must be intentional.

---

### R3. Refusal of Proxy Recognition
State Ledger refuses recognition entered on behalf of another individual.
Recognition must be owned by the individual with authority.

---

### R4. Refusal of Retrospective Editing
State Ledger refuses edits to past declarations.
Corrections must take the form of new declarations.

---

### R5. Refusal of Collective Recognition
State Ledger refuses recognition attributed to groups, committees, or consensus.
Recognition requires a single accountable owner.

---

### R6. Refusal of Interpretive Fields
State Ledger refuses free-form explanation fields tied to recognition.
Explanation delays acknowledgment.

---

### R7. Refusal of Action Coupling
State Ledger refuses to link recognition to:
- tasks
- plans
- workflows
- approvals

Recognition must stand independently of action.

---

### R8. Refusal of Optimization Pressure
State Ledger refuses metrics, scores, or incentives tied to recognition behavior.
Optimizing recognition distorts truth.

---

## Escalation Through Refusal
When State Ledger refuses an interaction:
- no alternative path is provided
- no workaround is suggested
- no override exists

The refusal itself is the forcing function.

Requests that attempt to bypass exclusions are refused.
See `constitution/state_ledger/STATE_EXCLUSIONS.md`.

---

## Relationship to Authority
State Ledger does not enforce authority.
It assumes authority exists.

When authority attempts to evade recognition, State Ledger refuses cooperation.

---

## Why Refusal Is Essential
Most epistemic failure occurs not through ignorance,
but through systems that accommodate avoidance.

State Ledger exists to remove that accommodation.

---

## Closing Statement
State Ledger preserves truth by refusing to make it easier.

If the system ever feels cooperative in moments of avoidance,
it has already failed.
