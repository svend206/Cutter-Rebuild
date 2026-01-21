---
doc_id: ui_verification_loop_checklist
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
tags: [ui, verification, checklist, context]
---

# UI Verification Loop Checklist (MVP Anchoring Document)

**Status:** Active / Anchoring Artifact

This document is the **procedural anchor** for building and verifying the UI required to falsify the locked MVP. It exists to prevent drift, scope creep, and accidental product design.

This checklist is used **once per MVP capability**. You will return to this document at the end of every loop.

No work is considered complete unless it passes this checklist.

---

## How This Document Is Used

* One MVP capability = one verification loop
* Loops are executed sequentially, not in parallel
* Each loop must be explicitly closed before the next begins
* This document is referenced at the **start and end** of every loop

---

## The Verification Loop (Repeatable Process)

### LOOP ENTRY CONDITIONS (Must All Be True)

* [ ] `MVP_CAPABILITIES_LOCKED.md` is unchanged and locked
* [ ] `context/MVP_VERIFICATION_GAP_ANALYSIS.md` identifies the capability as a **Verification Gap**
* [ ] No product UI, workflow, or optimization work is in progress
* [ ] Cursor is operating under a **no-invention, no-design** constraint

---

### STEP 1 — SPECIFICATION (NO CODE)

**Artifact:** `context/UI_VERIFICATION_SPEC.md`

For the target MVP capability:

* [ ] The spec describes how a human attempts to violate the guarantee
* [ ] The spec describes the minimum UI signals required to observe the outcome
* [ ] The spec lists explicit non-goals (what must NOT appear)
* [ ] No UI layout, navigation, styling, or workflows are described
* [ ] The spec is strictly verification-oriented

**Exit condition:** Spec is reviewed and approved without modification

---

### STEP 2 — IMPLEMENTATION (CODE, NARROWLY SCOPED)

**Artifacts:** UI code + tests (as applicable)

* [ ] Cursor implements **only** what the approved spec requires
* [ ] No additional UI elements are introduced
* [ ] No aggregation, interpretation, or guidance is added
* [ ] Any tests added are negative or invariant tests
* [ ] No unrelated refactors are performed

**Exit condition:** Implementation matches spec exactly

---

### STEP 3 — ADVERSARIAL VERIFICATION (HUMAN-IN-THE-LOOP)

* [ ] Attempt to violate the MVP guarantee via UI interaction
* [ ] Attempt to rush, skip steps, or misuse the system
* [ ] Attempt to induce comfort, inference, or guidance
* [ ] Observe whether silence and absence are preserved

**Pass condition:** The UI refuses to help violate the guarantee

---

### STEP 4 — LOOP CLOSURE

* [ ] MVP capability is now **UI-verifiable**
* [ ] `context/MVP_VERIFICATION_GAP_ANALYSIS.md` is updated
* [ ] Capability is moved from **Verification Gap** to **MVP-Satisfied**
* [ ] This checklist is reviewed for drift or ambiguity

**Exit condition:** Loop is explicitly closed

---

## Locked MVP Capability Index (Reference)

This list must **never be edited here**. It is copied verbatim from the locked MVP and exists only for loop tracking.

* **MVP-1** — Ops can perform work and emit exhaust
* **MVP-2** — Cutter Ledger preserves demonstrated operational reality
* **MVP-3** — Cutter Ledger is read-only with respect to meaning
* **MVP-4** — State Ledger supports explicit human recognition
* **MVP-5** — State continuity requires explicit reaffirmation
* **MVP-6** — Evidence may be referenced but never evaluated
* **MVP-7** — Separation between Ops, Cutter Ledger, and State Ledger is enforced
* **MVP-8** — Explicit, downstream-only Guild exhaust export
* **MVP-9** — System authority is document-governed and non-inventive
* **MVP-10** — Absence of action is a preserved, inspectable fact
* **MVP-11** — Ops enforces separation of execution and planning modes

---

## Anti-Drift Rules (Non-Negotiable)

* No loop may introduce product features
* No loop may improve usability beyond verification needs
* No loop may change MVP language
* No loop may combine multiple MVP capabilities
* No loop may skip adversarial verification

---

## Success Definition

This effort is complete when **all 11 MVP capabilities** are marked **MVP-Satisfied** *and* are adversarially verifiable via UI.

At that point, the system is not just implemented — it is **provable**.
