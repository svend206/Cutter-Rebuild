---
doc_id: phase_vii_work_charter
doc_type: spec
status: draft
version: 0.3
date: 2026-01-26
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - boot/PROJECT_PHASE_CONSTITUTION.md
  - planning/PHASE_VI_WORK_CHARTER.md
  - planning/PHASE_VI_LOOP_1.md
  - planning/PHASE_VI_LOOP_2.md
conflicts_with: []
tags: [phase, guarantees, charter, spec]
---

# Phase VII — Work Charter (Guarantees & Claim Boundaries)

Phase: VII — Guarantees & Claim Boundaries  
Status: Draft

---

## Intent

Phase VII exists to define **exactly what the system claims** and **exactly what it refuses to claim**.

No guarantee exists unless explicitly defined in this phase.

Silence outside the set of *considered claims* is meaningless; silence **within** the considered set is treated as explicit denial.

This phase does not implement guarantees.

---

## Allowed Work (This Phase Only)

During Phase VII, the project may define and document:

- explicit system guarantees (if any),
- explicit non-guarantees,
- preconditions required for each guarantee,
- conditions under which guarantees are violated,
- conditions under which guarantees are unverifiable,
- mandatory refusal semantics bound to all of the above.

All guarantees must be:

- **binary in outcome** (hold or refuse given preconditions),
- non-probabilistic,
- non-aspirational.

---

## Forbidden Work

Phase VII must not:

- imply safety, prevention, or protection,
- soften guarantees through “best effort” or likelihood language,
- define mitigation, recovery, or retry behavior,
- define implementation mechanisms,
- introduce scoring, grading, or confidence labels.

If a guarantee cannot be enforced via refusal, it must not be claimed.

---

## Required Artifacts (to Exit Phase VII)

Phase VII must produce the following:

1. **Guarantee Registry**
2. **Non-Guarantee Registry**
3. **Guarantee → Refusal Binding Table**
4. **Claim Consideration Log**
   - Exhaustive enumeration of claims considered
   - Each claim classified as:
     - Guaranteed
     - Explicitly Denied
     - Declared Out of Scope (with justification)
5. **Phase VII Adversarial Guarantee Audit Record**

---

## Refusal Semantics Inheritance

All refusals defined in Phase VII **must satisfy all Phase VI refusal invariants**.

Phase VII refusals are a **specialization of Phase VI refusals**, not a separate or weaker refusal system.

---

## Exit Condition (Human Judgment)

Phase VII ends only when a reviewer can say:

> “Every claim considered by this project is either explicitly guaranteed, explicitly denied, or explicitly declared out of scope — and all guarantees are refusal-backed.”
