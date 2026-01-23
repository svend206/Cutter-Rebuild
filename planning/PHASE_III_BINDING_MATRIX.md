---
doc_id: phase_iii_binding_matrix
doc_type: spec
status: active
version: 1.2
date: 2026-01-23
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/PROJECT_PHASE_CONSTITUTION.md, planning/PHASE_III_WORK_CHARTER.md]
conflicts_with: []
tags: [phase, binding, matrix, spec]
---

# Phase III — Binding Matrix

Phase: III — Binding  
Status: Draft (Intent-Locked)

---

## Purpose

This matrix declares which records become **durable, ordered, and irreversible**.

It answers only:
- what cannot be erased
- what cannot be rewritten
- how supersession is allowed without deletion

It does not define storage, access, behavior, or meaning.

---

## Binding Declarations by Record Type

### 1) Action Record

- Append-only: **Yes**
- Irreversible once written: **Yes**
- Supersession allowed: **No**
- Deletion permitted: **No**
- Compaction/merging permitted: **No**

Notes:
- Actions represent that something occurred.
- Later records may reference actions, but actions themselves are never replaced.

---

### 2) Observation Record

- Append-only: **Yes**
- Irreversible once written: **Yes**
- Supersession allowed: **No**
- Deletion permitted: **No**
- Compaction/merging permitted: **No**

Notes:
- Observations preserve what was observed at a time.
- Subsequent observations do not invalidate earlier ones.

---

### 3) Declaration Record

- Append-only: **Yes**
- Irreversible once written: **Yes**
- Supersession allowed: **Yes**
- Deletion permitted: **No**
- Compaction/merging permitted: **No**

Supersession constraints:
- Supersession occurs only via a new record.
- Prior declarations remain inspectable.
- Supersession does not imply error or correctness.

---

### 4) Reaffirmation / Reclassification Record

- Append-only: **Yes**
- Irreversible once written: **Yes**
- Supersession allowed: **Yes**
- Deletion permitted: **No**
- Compaction/merging permitted: **No**

Supersession constraints:
- A reaffirmation or reclassification references a prior declaration.
- It does not erase or overwrite the prior record.
- Multiple reaffirmations may coexist.

---

### 5) Absence / Non-Occurrence Record

- Append-only: **Yes**
- Irreversible once written: **Yes**
- Supersession allowed: **No**
- Deletion permitted: **No**
- Compaction/merging permitted: **No**

Notes:
- Absence records preserve that something did not occur within an explicit, bounded, immutable window.
- Contradiction-narrowing records may reference a prior absence record without erasing it.
- Later occurrence does not invalidate the absence record.

---

### 6) Refusal Record

- Append-only: **Yes**
- Irreversible once written: **Yes**
- Supersession allowed: **No**
- Deletion permitted: **No**
- Compaction/merging permitted: **No**

Notes:
- Refusals must remain durable and identify the refused action.
- Later permission or action does not erase a prior refusal.

---

### 7) Reference / Link Record

- Append-only: **Yes**
- Irreversible once written: **Yes**
- Supersession allowed: **Yes**
- Deletion permitted: **No**
- Compaction/merging permitted: **No**

Supersession constraints:
- Supersession may alter which reference is highlighted.
- Original references remain inspectable.
- References never imply causality or hierarchy.
- Multiple supersession designations may coexist and remain equally visible.

---

### 8) Correction / Supersession Designation Record

- Append-only: **Yes**
- Irreversible once written: **Yes**
- Supersession allowed: **Yes**
- Deletion permitted: **No**
- Compaction/merging permitted: **No**

Supersession constraints:
- Supersession is a designation, not an evaluation.
- Prior records are not erased or modified.
- Multiple supersession designations may coexist and remain equally visible.

---

## Global Binding Invariants

- No record declared append-only may be edited in place.
- No record declared irreversible may be deleted.
- Supersession never erases history.
- Ordering between records must remain explicit and inspectable.
- Silence and non-occurrence remain visible over time.

---

## Explicit Non-Decisions

This matrix does not decide:
- how records are stored
- how long records are retained
- how records are queried
- how records are presented
- how records influence action

Those decisions belong to later phases.

---

## Explicit Deferrals (Binding Boundary)

Deferred risks owned by Phase IV — Exposure:
- Record volume / obscuring (record flooding)
- Practical human inspectability / accessibility

Phase III guarantees meanwhile:
- durability
- irreversibility
- ordering
- non-erasure

Phase III explicit non-solutions:
- limits or throttling
- filtering or summarization
- surfacing rules
- formats or tooling
- user interfaces

---

## Phase IV Entry Obligations

Phase IV Work Charter MUST include explicit handling of the deferred risks listed above.  
Phase IV may not be closed until an adversarial audit confirms these deferrals are addressed.

---

## Exit Readiness

This matrix is complete when a reviewer can say:
- “I know exactly what cannot be undone.”
- “I can reconstruct history even after correction.”
- “Nothing important can be quietly removed.”
