---
doc_id: phase_iv_exposure_views_catalog
doc_type: spec
status: active
version: 1.0
date: 2026-01-23
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/PROJECT_PHASE_CONSTITUTION.md, planning/PHASE_IV_WORK_CHARTER.md, planning/PHASE_IV_EXPOSURE_INVARIANTS.md]
conflicts_with: []
tags: [phase, exposure, views, catalog, spec]
---

# Phase IV — Exposure Views Catalogue

This catalogue defines lawful classes of exposure views and reports.
It describes what may be exposed without interpretation or authority.

---

## Mandatory Properties of All Exposure Views

- Ordering:
  - If ordering exists, it must be neutral and must not imply priority, importance, or recommendation.
  - The ordering basis must be stated; semantic ordering is forbidden.
- Completeness:
  - Views must state whether they claim completeness or explicitly deny it.
  - Absence of records must not be presented as absence of events.
- Expectations:
  - Views that depend on expectations must explicitly state whether expectations were defined.
  - Undefined expectations must be made visible as such.
- Association:
  - Subject-centric association must be explicitly scoped to explicit references only.
  - Views must not imply exhaustive association unless stated.
- Defaults:
  - No exposure view may be default-selected.
  - Any initial view must be the result of explicit human choice.
- Sequencing:
  - Sequence must not imply narrative, resolution, trend, or correctness.

---

## 1) Event-Centric Views (“what happened”)

**Purpose**  
Expose events as recorded, in neutral ordering.

**What it exposes**  
Events, timestamps, and sequencing without collapse.

**What it explicitly does NOT imply**  
Importance, success, failure, or what should happen next.
Ordering does not imply priority, narrative, or correctness.

**Invariant alignment notes**  
Must preserve ordering, avoid collapse, and keep originals inspectable.

---

## 2) Non-Event / Absence Views (“what did not happen”)

**Purpose**  
Expose explicit non-occurrence records.

**What it exposes**  
Absence records and their bounded windows, without interpretation.

**What it explicitly does NOT imply**  
Safety, fault, urgency, or resolution.

**Invariant alignment notes**  
Must show absence explicitly and avoid rendering silence as reassurance.

---

## 3) Time-Bounded Views (“between X and Y”)

**Purpose**  
Expose records within a specified time window.

**What it exposes**  
All records that fall within the stated bounds, with ordering preserved.

**What it explicitly does NOT imply**  
Priority, completeness, or significance beyond the stated bounds.
Absence of records within the window does not imply absence of events.

**Invariant alignment notes**  
Must make bounds explicit and keep originals accessible.

---

## 4) Subject-Centric Views (“everything related to this subject”)

**Purpose**  
Expose records associated with a named subject via explicit reference.

**What it exposes**  
Related records across time without collapsing or ranking.

**What it explicitly does NOT imply**  
Exhaustive association, causality, hierarchy, or summary judgment.

**Invariant alignment notes**  
Must retain independent meaning of records and avoid hidden aggregation.

---

## 5) Declaration History Views (“what was declared and how it evolved”)

**Purpose**  
Expose declaration sequences and supersession over time.

**What it exposes**  
Declarations, reaffirmations, reclassifications, and their ordering.

**What it explicitly does NOT imply**  
Correctness, endorsement, or finality of any declaration.
Sequence does not imply resolution or correctness.

**Invariant alignment notes**  
Must keep prior declarations inspectable and show supersession without erasure.

---

## 6) Refusal Views (“what was attempted but not performed”)

**Purpose**  
Expose refusal records and the refused actions.

**What it exposes**  
Refusals with their stated refused actions, in sequence.

**What it explicitly does NOT imply**  
Fault, blame, or invalidity of the attempted action.

**Invariant alignment notes**  
Must keep refusals durable and visible without softening.

---

## 7) Supersession / Evolution Views (“how records relate over time without collapse”)

**Purpose**  
Expose supersession designations and record evolution.

**What it exposes**  
Supersession links and the coexisting records they connect.

**What it explicitly does NOT imply**  
Replacement, correctness, or hierarchy among records.
Sequence does not imply resolution or correctness.

**Invariant alignment notes**  
Must keep superseded records visible and avoid collapsing history.

---

## 8) Silence / Gap Views (“where nothing exists but might have been expected”)

**Purpose**  
Expose gaps or silences as explicit absence.

**What it exposes**  
Intervals or contexts with no records, with expectations stated or explicitly undefined.

**What it explicitly does NOT imply**  
Failure, success, or the need for action.
Absence of records does not imply absence of events.

**Invariant alignment notes**  
Must distinguish “no data” from “nothing happened” and avoid reassurance.

---

## View Neutrality Guarantee

Exposure views are projections, not interpretations.  
Any implementation that violates the mandatory properties above is invalid.
