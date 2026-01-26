---
doc_id: PROJECT_PHASE_CONSTITUTION_AMENDMENT_V8_CONSTITUTIONAL_AMENDMENT_AUTHORIZATION
doc_type: constitutional_amendment
status: draft
version: 1.0
date: 2026-01-26
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - boot/BOOT_CONTRACT.md
  - boot/PROJECT_PHASE_CONSTITUTION.md
  - constitution/CONSTITUTION_AUTHORITY.md
conflicts_with: []
tags: [constitution, amendment, phase_xi, governance]
---

# CONSTITUTIONAL AMENDMENT v8
## Authorization of Constitutional Amendments During Phase XI

---

## Amendment Preconditions (Satisfied)

- **Proposed change is written in full** — see Full Replacement Text.
- **Reason for change is stated plainly** — see Reason for Change.
- **Impact on all phases is considered** — see Impact Analysis.
- **Compatibility with the Constitution is explicitly affirmed** — see Compatibility Statement.
- **Amendments by implication are forbidden** — all affected text is replaced in full.

---

## Sponsor and Authority

- **Named Human Sponsor:** Erik
- **Named Human Approver:** Erik

---

## Recorded Adversarial Review

- **Review Record:** planning/PROJECT_PHASE_CONSTITUTION_AMENDMENT_V8_AUDIT.md
- **Outcome Required:** PASS

This amendment is not active until an adversarial review records **PASS**.

---

## Reason for Change

Phase XI currently authorizes implementation but does not explicitly authorize constitutional amendments. This creates ambiguity when a named human needs to strengthen constraints or close ambiguity in a canon during implementation.

Constitutional amendments are a governance act, not a feature. The project needs an explicit, auditable path to perform them without implying new authority or bypassing phase discipline.

---

## Compatibility Statement

This amendment:
- does not weaken any Global Invariant,
- does not reduce refusal requirements,
- does not automate judgment or authority,
- does not bypass phase discipline,
- does not resolve tension through vagueness.

If any conflict with the Constitution is discovered, **this amendment is void**.

---

## Full Prior Text (Being Replaced)

The following section is replaced **in full**:

> #### Phase XI — Implementation (Execution)
>
> ##### Purpose
>
> Phase XI authorizes implementation **only** as a realization of constraints defined in Phases VI–X.
>
> ---
>
> ##### Required Artifacts
>
> 1. **Constraint Coverage Matrix (Authoritative)**
>    - Mapping every constraint from Phases VI–X to one of:
>      - Implemented → component(s) named
>      - Explicitly Unimplemented → reason + adversarial acknowledgment
>
> 2. **Implementation Trace Map**
>    - For each implemented constraint:
>      - which components realize it
>      - where refusal occurs
>      - where absence is surfaced
>
> 3. **Phase XI Adversarial Implementation Audit Record**
>    - Adversarial review attempting to show:
>      - meaning smuggled in through behavior
>      - guarantees implied by UX
>      - refusals inconsistent
>      - omissions hidden
>
> Selective implementation is forbidden.

---

## Full Replacement Text

#### Phase XI — Implementation (Execution)

##### Purpose

Phase XI authorizes implementation **only** as a realization of constraints defined in Phases VI–X.

Phase XI also authorizes constitutional amendments **only** when a named human explicitly requests the change and the amendment strengthens constraints or closes ambiguity without adding new authority.

---

##### Allowed Work

During Phase XI, the project may:

- implement constraints defined in Phases VI–X
- perform constitutional amendments that:
  - strengthen constraints or close ambiguity
  - do not authorize new capabilities, guarantees, or authority
  - follow the constitutional amendment ceremony (full prior text, full replacement text, justification, sponsor, approver, recorded adversarial review)
  - satisfy governance requirements (decision log entry when required; `DIRECTORY.md` updates for new documents)

---

##### Required Artifacts

1. **Constraint Coverage Matrix (Authoritative)**
   - Mapping every constraint from Phases VI–X to one of:
     - Implemented → component(s) named
     - Explicitly Unimplemented → reason + adversarial acknowledgment

2. **Implementation Trace Map**
   - For each implemented constraint:
     - which components realize it
     - where refusal occurs
     - where absence is surfaced

3. **Phase XI Adversarial Implementation Audit Record**
   - Adversarial review attempting to show:
     - meaning smuggled in through behavior
     - guarantees implied by UX
     - refusals inconsistent
     - omissions hidden

If a constitutional amendment is performed during Phase XI, its amendment record and adversarial audit must be created and registered in `DIRECTORY.md` in the same change.

Selective implementation is forbidden.

---

## Impact Analysis (All Phases)

- **Phases I–X:** Unchanged.
- **Phase XI:** Explicitly permits constitutional amendments that strengthen constraints and do not add authority.
- **Phases XII–XVI:** Unchanged.

---

## Amendment Closure

This amendment becomes authoritative only after:

- adversarial review records PASS,
- amendment is committed and tagged.

Until then, the prior Phase XI text remains in force.
