---
doc_id: PROJECT_PHASE_CONSTITUTION_AMENDMENT_V3_GUARANTEES_PHASE
doc_type: constitutional_amendment
status: draft
version: 1.0
date: 2026-01-25
owner: Erik
authoring_agent: architect
supersedes: [PROJECT_PHASE_CONSTITUTION_AMENDMENT_V2]
superseded_by: []
authoritative_sources:
  - boot/BOOT_CONTRACT.md
  - constitution/CONSTITUTION_AUTHORITY.md
conflicts_with: []
tags: [constitution, amendment, phases, guarantees]
---

# CONSTITUTIONAL AMENDMENT v3  
## Insertion of a Dedicated Guarantees Phase

---

## Amendment Preconditions (Satisfied)

- **Proposed change is written in full** — see Full Replacement Text.
- **Reason for change is stated plainly** — see Justification.
- **Impact on all phases is considered** — see Impact Analysis.
- **Compatibility with the Constitution is explicitly affirmed** — see Compatibility Statement.
- **Amendments by implication are forbidden** — no implicit changes exist; all affected text is replaced in full.

---

## Sponsor and Authority

- **Named Human Sponsor:** Erik  
- **Named Human Approver:** Erik  

---

## Recorded Adversarial Review

- **Reviewer:** To be assigned (must not be the primary author)
- **Record Location:** planning/PROJECT_PHASE_CONSTITUTION_AMENDMENT_V3_AUDIT.md
- **Status:** Pending

No phase transition is authorized until this review records **PASS**.

---

## Reason for Change (Plain Statement)

An adversarial review of Phases VI–X revealed that **explicit system guarantees** lack a dedicated, constitutionally sanctioned phase.

As a result:
- guarantees risk being implied rather than declared,
- reliance boundaries risk being inferred rather than bound,
- commercialization language risks inventing claims post hoc,
- abuse visibility risks being conflated with prevention promises.

This amendment introduces a **dedicated phase for guarantees and non-guarantees**, ensuring that all claims the system makes—or refuses to make—are explicit, refusal-backed, and non-implied.

This change strengthens, rather than weakens, epistemic safety.

---

## Statement of Compatibility

This amendment:

- does **not** weaken any Global Invariant,
- does **not** reduce refusal requirements,
- does **not** automate judgment or authority,
- does **not** bypass phase discipline,
- does **not** resolve tension through vagueness,
- preserves Phase VI operability constraints unchanged,
- preserves abuse visibility as non-preventive and non-moralized.

If any conflict with the Constitution is later discovered, **this amendment is void**.

---

## Full Prior Text (Being Replaced — In Full)

The following section of the Project Phase Constitution is replaced **in full**:

> **Phase VII — Abuse & Adversarial Resistance (Definition Only)**  
> **Phase VIII — Commercialization Boundaries (Definition Only)**  
> **Phase IX — Exit, Shutdown, and Irreversibility (Definition Only)**  
> **Phase X — Implementation (Execution)**  
>
> (As defined in Constitutional Amendment v2.)

No other text is modified.

---

## Full Replacement Text

---

### **Phase VII — Guarantees & Claim Boundaries (Definition Only)**

#### Purpose

Phase VII exists to define **exactly what the system claims** and **exactly what it refuses to claim**.

This phase makes all guarantees:
- explicit,
- conditional,
- refusal-backed,
- and non-implied.

Silence is treated as denial.

This phase does **not** implement guarantees.

---

#### Allowed Work

During Phase VII, the project may **define and document**:

- explicit system guarantees (if any),
- explicit non-guarantees,
- preconditions required for each guarantee,
- conditions under which guarantees are violated,
- conditions under which guarantees are unverifiable,
- mandatory refusal semantics bound to all of the above.

All guarantees must be:
- binary (hold or refuse),
- non-probabilistic,
- non-aspirational.

---

#### Forbidden Work

Phase VII must not:

- imply safety, prevention, or protection,
- soften guarantees through “best effort” language,
- define mitigation or recovery behavior,
- define implementation mechanisms,
- introduce scoring, grading, or confidence language,
- promise outcomes or correctness by default.

If a guarantee cannot be enforced via refusal, it must not be claimed.

---

#### Required Artifacts

- Guarantee Registry  
- Non-Guarantee Registry  
- Guarantee → Refusal Binding Table  
- Phase VII Adversarial Guarantee Audit Record  

---

#### Exit Gate

Phase VII may be exited only when a reviewer can say:

> “Every claim this system makes is explicit, conditional, and refusal-backed — and nothing else is implied.”

---

---

### **Phase VIII — Abuse & Adversarial Resistance (Definition Only)**

*(Text identical to prior Phase VII, renumbered only)*

#### Purpose

Phase VIII exists to define how misuse, coercion, and adversarial behavior
are **made visible rather than prevented, moralized, or denied**.

This phase does not create guarantees.

---

#### Allowed Work

During Phase VIII, the project may **define and document**:

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
- classify intent,
- enforce morality,
- suppress uncomfortable usage,
- implement controls or mitigations.

---

#### Required Artifacts

- Adversarial Misuse Catalog  
- Abuse Visibility Boundary  
- Residual Harm Disclosure  
- Phase VIII Adversarial Audit Record  

---

#### Exit Gate

Phase VIII may be exited only when a reviewer can say:

> “If this is abused, the limits of visibility are explicit and not denied.”

---

---

### **Phase IX — Commercialization Boundaries (Definition Only)**

*(Renumbered; text unchanged)*

---

### **Phase X — Exit, Shutdown, and Irreversibility (Definition Only)**

*(Renumbered; text unchanged)*

---

### **Phase XI — Implementation (Execution)**

*(Renumbered; text unchanged, with references updated to Phases VI–X)*

Implementation is authorized **only** as a realization of constraints defined in Phases VI–X.

---

## Impact Analysis (All Phases)

- **Phases I–V:** Unchanged.
- **Phase VI (Operability):** Unchanged; remains constraint-only.
- **New Phase VII:** Introduces explicit claim discipline; no new authority.
- **Phase VIII (Abuse):** Narrowed and clarified; no promises introduced.
- **Commercialization & Exit Phases:** Strengthened by upstream clarity.
- **Implementation Phase:** Gains explicit traceability for claims vs denials.

No phase gains new power.  
Several phases lose ambiguity.

---

## Limits Compliance Check

- ❌ No Global Invariants weakened  
- ❌ No refusal requirements reduced  
- ❌ No authority automated  
- ❌ No judgment encoded  
- ❌ No tension resolved through vagueness  

This amendment is **strictly constraining**, not enabling.

---

## Amendment Closure (Pending)

This amendment is **not active** until:

- adversarial review is recorded,
- outcome is PASS,
- amendment is committed and tagged.

Until then, the prior phase structure remains authoritative.

---

## Closing Statement

This amendment exists to make **over-claiming structurally difficult**.

If following it feels slow or heavy,
that friction is intentional.

Guarantees are expensive on purpose.
