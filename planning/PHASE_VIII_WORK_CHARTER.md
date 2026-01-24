---
doc_id: phase_viii_work_charter
doc_type: spec
status: draft
version: 1.0
date: 2026-01-26
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - constitution/CONSTITUTION_AUTHORITY.md
  - boot/PROJECT_PHASE_CONSTITUTION.md
  - planning/PHASE_VI_WORK_CHARTER.md
  - planning/PHASE_VII_WORK_CHARTER.md
conflicts_with: []
tags: [phase, abuse, adversarial, charter, spec]
---

# Phase VIII — Abuse & Adversarial Resistance

## Work Charter (Authoritative, Definition‑Only)

---

## 1. Authority and Scope

This Work Charter governs **all work performed in Phase VIII**.

It derives authority from:

* the Constitution,
* the Project Phase Constitution,
* Phase VI (Operability), and
* Phase VII (Guarantees & Claim Boundaries).

If any conflict exists, **this charter is void** and work must refuse.

Phase VIII is **definition‑only**. No implementation, mitigation, prevention, control, or enforcement work is authorized.

---

## 2. Purpose of Phase VIII

Phase VIII exists to define how **misuse, coercion, and adversarial behavior** are:

* made **explicitly visible**, or
* **explicitly left unobserved**,

**without implying**:

* prevention,
* detection competence,
* safety,
* deterrence,
* harm reduction,
* or system protection.

Phase VIII does **not** reduce abuse.
It ensures abuse is **not denied**.

---

## 3. Binding Constraints (Inherited)

### 3.1 Zero‑Guarantee Inheritance (from Phase VII)

* The system asserts **no guarantees**.
* Abuse visibility MUST NOT imply:

  * that abuse will be detected,
  * that surfaced abuse is representative,
  * that absence of abuse signals safety,
  * or that visibility implies completeness.

Any wording that could be reasonably interpreted as competence or coverage is forbidden.

---

### 3.2 Failure vs Abuse Separation (from Phase VI)

Phase VIII MUST NOT:

* relabel operational failure, uncertainty, or refusal as abuse,
* treat degraded operation as adversarial behavior,
* attribute intent to failures,
* or imply misuse where the system cannot know intent.

Operational uncertainty remains governed by Phase VI.
Abuse is a **separate descriptive category**, not a fallback.

---

## 4. Allowed Work

During Phase VIII, the project may **define and document**:

1. **Adversarial Misuse Catalog**

   * Descriptive enumeration of misuse and abuse patterns
   * No intent attribution
   * No moral language
   * No likelihood or prevalence claims

2. **Abuse Visibility Boundary**

   * Which misuse patterns are surfaced
   * Which are not surfaced
   * Visibility must be explicit, not inferred

3. **Residual Harm Disclosure**

   * Explicit statement of harms that may occur
   * Explicit statement of harms the system does not surface
   * Explicit acknowledgment of blind spots

4. **Justification for Non‑Visibility**

   * Required where visibility is possible but not provided
   * Justifications MUST NOT rely on:

     * cost
     * performance
     * convenience
     * user preference
     * optimism

All outputs must be **descriptive, declarative, and refusal‑compatible**.

---

## 5. Forbidden Work

Phase VIII MUST NOT:

* promise prevention, protection, or safety
* classify intent, morality, or blame
* introduce controls, mitigations, throttles, or enforcement
* imply deterrence through visibility
* soften harm through reassurance language
* imply completeness, coverage, or representativeness
* rely on silence or omission to imply safety
* implement logging, monitoring, or tooling
* reference future implementation as assurance

If any output answers the question

> “Does the system stop this?”

then the output is invalid.

---

## 6. Language Discipline

### 6.1 Required Properties

All Phase VIII language MUST:

* remain present‑tense and descriptive
* avoid future‑tense implications
* avoid conditional safety framing
* survive adversarial reading without softening

### 6.2 Forbidden Implications (Non‑Exhaustive)

Language MUST NOT imply:

* "we would know if"
* "this helps detect"
* "this reduces risk"
* "this discourages"
* "this protects"
* "this is designed to prevent"

Visibility is **not** competence.
Enumeration is **not** coverage.

---

## 7. Required Artifacts

Phase VIII must produce exactly the following:

1. **Adversarial Misuse Catalog**
2. **Abuse Visibility Boundary**
3. **Residual Harm Disclosure**
4. **Phase VIII Adversarial Audit Record**

No additional artifacts are authorized.

---

## 8. Exit Gate

Phase VIII may be exited only when an adversarial reviewer can truthfully say:

> “If this system is abused, the limits of what it shows — and does not show — are explicit and not denied.”

If any reviewer can extract:

* implied safety,
* implied detection,
* implied prevention,
* or implied responsibility transfer,

then Phase VIII has failed and must be corrected.

---

## 9. Refusal Obligation

Any work that:

* exceeds this scope,
* introduces implication by example,
* or weakens refusal posture

MUST be refused immediately.

Refusal is compliance.

---

## 10. Closure Rule

Phase VIII closes only through:

* completed artifacts,
* a recorded adversarial audit,
* and explicit pass/fail determination.

No conditional passes.
No partial exits.
