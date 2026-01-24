---
doc_id: PROJECT_PHASE_CONSTITUTION_AMENDMENT_V4_GUARANTEES_PHASE
doc_type: constitutional_amendment
status: draft
version: 1.0
date: 2026-01-26
owner: Erik
authoring_agent: architect
supersedes:
  - PROJECT_PHASE_CONSTITUTION_AMENDMENT_V3_GUARANTEES_PHASE
superseded_by: []
authoritative_sources:
  - boot/BOOT_CONTRACT.md
  - boot/PROJECT_PHASE_CONSTITUTION.md
  - constitution/CONSTITUTION_AUTHORITY.md
conflicts_with: []
tags: [constitution, amendment, phases, guarantees]
---

# CONSTITUTIONAL AMENDMENT v4  
## Insertion of a Dedicated Guarantees Phase (Auditable and Refusal-Bound)

---

## Amendment Preconditions (Satisfied)

- **Proposed change is written in full** — see Full Replacement Text.
- **Reason for change is stated plainly** — see Justification.
- **Impact on all phases is considered** — see Impact Analysis.
- **Compatibility with the Constitution is explicitly affirmed** — see Compatibility Statement.
- **Amendments by implication are forbidden** — all affected phase text is replaced in full.

---

## Sponsor and Authority

- **Named Human Sponsor:** Erik  
- **Named Human Approver:** Erik  

---

## Recorded Adversarial Review

- **Reviewer:** Opus (adversarial auditor)
- **Review Record:** planning/PROJECT_PHASE_CONSTITUTION_AMENDMENT_V4_AUDIT.md
- **Outcome Required:** PASS

This amendment is not active until an adversarial review records **PASS**.

---

## Reason for Change (Plain Statement)

Prior versions of the Project Phase Constitution did not provide a dedicated, auditable location for defining what the system explicitly **guarantees** and explicitly **does not guarantee**.

As a result:
- guarantees risked being implied rather than declared,
- refusal semantics risked being uneven across phases,
- commercialization and reliance could invent claims post hoc,
- abuse-visibility work risked being conflated with promises of prevention.

This amendment introduces a **dedicated Guarantees phase** that is declarative only, refusal-bound, and explicitly inherits Phase VI refusal semantics, making over-claiming structurally difficult.

---

## Compatibility Statement

This amendment:

- does **not** weaken any Global Invariant,
- does **not** reduce refusal requirements,
- does **not** automate judgment or authority,
- does **not** bypass phase discipline,
- does **not** resolve tension through vagueness.

If any conflict with the Constitution is discovered, **this amendment is void**.

---

## Full Prior Text (Replaced in Full)

The following section of the Project Phase Constitution is replaced **in full**:

> **Phase VII — Abuse & Adversarial Resistance (Definition Only)**  
> **Phase VIII — Commercialization Boundaries (Definition Only)**  
> **Phase IX — Exit, Shutdown, and Irreversibility (Definition Only)**  
> **Phase X — Implementation (Execution)**  
>
> (As defined in Constitutional Amendment v2.)

No other constitutional text is modified.

---

## Full Replacement Text

---

### **Phase VII — Guarantees & Claim Boundaries (Definition Only)**

#### Purpose

Phase VII exists to define **exactly what the system claims** and **exactly what it refuses to claim**.

No guarantee exists unless explicitly defined in this phase.

Silence outside the set of *considered claims* is meaningless; silence **within** the considered set is treated as explicit denial.

This phase does not implement guarantees.

---

#### Allowed Work

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

#### Forbidden Work

Phase VII must not:

- imply safety, prevention, or protection,
- soften guarantees through “best effort” or likelihood language,
- define mitigation, recovery, or retry behavior,
- define implementation mechanisms,
- introduce scoring, grading, or confidence labels.

If a guarantee cannot be enforced via refusal, it must not be claimed.

---

#### Required Artifacts

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

#### Refusal Semantics Inheritance

All refusals defined in Phase VII **must satisfy all Phase VI refusal invariants**.

Phase VII refusals are a **specialization of Phase VI refusals**, not a separate or weaker refusal system.

---

#### Exit Gate

Phase VII may be exited only when a reviewer can say:

> “Every claim considered by this project is either explicitly guaranteed, explicitly denied, or explicitly declared out of scope — and all guarantees are refusal-backed.”

---

---

### **Phase VIII — Abuse & Adversarial Resistance (Definition Only)**

#### Purpose

Phase VIII exists to define how misuse, coercion, and adversarial behavior are **made visible or explicitly left unobserved**, without implying prevention or safety.

This phase does not create guarantees.

---

#### Allowed Work

During Phase VIII, the project may define and document:

- abuse and misuse scenarios,
- incentive and economic attack patterns,
- which abuse scenarios are surfaced explicitly,
- which abuse scenarios remain possible without system-level visibility,
- explicit explanations for why visibility is not provided.

All distinctions must be descriptive, not evaluative.

---

#### Forbidden Work

Phase VIII must not:

- promise prevention or safety,
- classify intent or morality,
- suppress uncomfortable usage,
- implement controls or mitigations.

Choosing not to surface abuse that **could be surfaced** requires explicit justification in the **Residual Harm Disclosure**.  
Convenience, cost, performance, or user preference are **not valid justifications**.

---

#### Required Artifacts

- Adversarial Misuse Catalog  
- Abuse Visibility Boundary  
- Residual Harm Disclosure  
- Phase VIII Adversarial Audit Record  

---

#### Exit Gate

Phase VIII may be exited only when a reviewer can say:

> “If this system is abused, the limits of visibility are explicit and not denied.”

---

---

### **Phase IX — Commercialization Boundaries (Definition Only)**

#### Purpose

Phase IX defines constraints on how the system may be described, marketed, sold, demonstrated, or represented externally.

---

#### Required Artifacts

- Claim Consistency Check against Phase VII
- Prohibited Claim List
- Demonstration Constraint Statement

No commercial representation may introduce claims not present in Phase VII.

---

---

### **Phase X — Exit, Shutdown, and Irreversibility (Definition Only)**

#### Purpose

Phase X defines irreversible actions and exit conditions, including shutdown semantics.

---

#### Required Artifacts

- Irreversibility Register
- Shutdown Disclosure Statement

No exit behavior may imply guarantees not defined in Phase VII.

---

---

### **Phase XI — Implementation (Execution)**

#### Purpose

Phase XI authorizes implementation **only** as a realization of constraints defined in Phases VI–X.

---

#### Required Artifacts

- **Constraint Coverage Matrix**
  - Demonstrating that all constraints from Phases VI–X are:
    - realized, or
    - explicitly deferred with adversarial review

Selective implementation is forbidden.

---

## Impact Analysis (All Phases)

- **Phases I–V:** Unchanged.
- **Phase VI:** Unchanged; refusal and operability semantics preserved.
- **Phase VII:** New; introduces explicit, auditable claim discipline.
- **Phase VIII:** Clarified; prevents “chosen invisibility.”
- **Phases IX–X:** Strengthened through explicit linkage to guarantees.
- **Phase XI:** Coverage requirement added; no authority expansion.

---

## Renumbering Notice

All prior references to Phases VII–X are **void** and non-authoritative until updated to reflect this amendment.

---

## Amendment Closure

This amendment becomes authoritative only after:

- adversarial review records PASS,
- amendment is committed and tagged.

Until then, the prior phase structure remains in force.

---

## Closing Statement

This amendment exists to make **over-claiming detectable, auditable, and expensive**.

Guarantees are allowed —  
but only where refusal is stronger than promise.
