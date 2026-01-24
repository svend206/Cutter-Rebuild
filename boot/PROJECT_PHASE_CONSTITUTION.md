---
doc_id: project_phase_constitution
doc_type: spec
status: active
version: 1.0
date: 2026-01-22
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/BOOT_CONTRACT.md, constitution/CONSTITUTION_AUTHORITY.md]
conflicts_with: []
tags: [governance, phases, spec]
---

# Project Phase Constitution

## Purpose of This Constitution

This document defines the **law governing how this project is allowed to evolve**.

It is:
- timeless
- authoritative
- binding on all humans and agents
- written to be readable by non-programmers

This document does not describe what the project currently is.  
It defines what the project is **allowed to become**.

---

## Who This Constitution Governs

This Constitution governs:
- all human contributors
- all artificial agents
- all future maintainers
- any party acting with authority over the project

Compliance is mandatory.  
Ignorance is not a defense.

---

## How to Read This Document

This document is meant to be read **top to bottom**.

Earlier sections override later sections.  
Global rules override phase-specific rules.

If something feels convenient but unclear, assume it is forbidden.

---

## Constitutional Supremacy and Direction

### Constitutional Supremacy (Non-Negotiable)

This document is authoritative **only within the bounds of the Constitution**.

The Constitution is the highest authority.

This document:
- takes its direction from the constitutional documents
- implements constitutional intent at the project-phase level
- may not reinterpret, narrow, soften, or override any constitutional rule

If any conflict exists:

**The Constitution wins. Always.**

---

### Interpretation Rule

If this document appears to allow something that a constitutional document forbids,  
the allowance in this document is **void**, even if written explicitly.

Silence in this document does **not** imply permission if the Constitution speaks.

---

### Duty of Refusal

Any human or agent operating under this document has an affirmative duty to:
- detect conflicts with the Constitution
- refuse to proceed when a conflict exists
- state the refusal plainly and durably

Proceeding “in the spirit of” this document while violating the Constitution is a **hard violation**.

---

### Scope Clarification

This document governs:
- phase progression
- allowed and forbidden kinds of work
- required artifacts
- exit gates

This document does **not** govern:
- epistemic rules already bound by the Constitution
- ledger semantics
- authority models
- interpretation boundaries

Those are constitutional territory.

---

### Non-Escalation Rule

This document may not be amended to:
- grant powers the Constitution withholds
- weaken constitutional safeguards
- create exceptions “for practicality”
- resolve tension by compromise

Any such amendment is invalid on its face.

---

## Global Invariants (Always True, All Phases)

The following rules apply in **every phase**, without exception.

No phase, feature, schedule, or person may override them.

---

### 1. The Permanent “Never” List

The system must **never**:
- automate blame, punishment, or moral judgment
- encode “good,” “bad,” “healthy,” “failing,” or similar value judgments
- close the loop automatically from observation to action
- hide uncertainty, disagreement, or missing information
- pretend silence means “everything is fine”
- replace human responsibility with system authority

If any of these occur, the system is constitutionally broken.

---

### 2. Separation of Execution From Interpretation

Execution means doing work.  
Interpretation means deciding what that work means.

These must remain structurally separate.

The system may:
- capture what happened
- preserve it faithfully
- show it clearly

The system must not:
- decide what it means
- decide what should be done
- decide who is at fault
- decide whether something is acceptable

Meaning belongs to humans.

---

### 3. Explicit Human Authority Is Required

For anything that:
- declares a condition
- assigns responsibility
- recognizes a situation as continuing or changing

A **named human** must do it explicitly.

Authority may not be:
- implied
- inferred
- averaged
- delegated without clarity

If no human is on the hook, the system must show that clearly.

---

### 4. Absence and Silence Must Remain Visible

The system must make the following visible:
- missing data
- no response
- no decision
- no update
- no confirmation

Silence is a fact.  
Absence is a fact.

The system must never convert:
“nothing happened”  
into  
“everything is okay”.

---

### 5. Deterministic, Explicit Refusals

When the system cannot act, it must:
- refuse clearly
- refuse the same way every time
- state why in plain language
- leave a durable record of the refusal

Silent failure or partial action is forbidden.

---

### 6. No Known Deferral Rule (Hard Invariant)

If all of the following are true:
- a problem is known
- it is safe to fix now
- it is within scope
- it is within authority

Then it **must be fixed now**.

“OK for now” is not allowed.

---

### 7. Reality Is Preserved, Not Smoothed

The system must not:
- average away discomfort
- normalize repeated problems
- make long-lasting issues feel routine
- let time erase meaning

Time passing does not resolve anything by itself.

---

### 8. No Hidden Collapsing of Information

The system must not secretly:
- summarize without trace
- aggregate without provenance
- replace detail with comfort
- trade clarity for neatness

If information is collapsed, the collapse must be visible and inspectable.

---

### 9. Humans Remain Accountable

The system may support humans.
It may inform humans.
It may constrain humans.

It must never:
- take responsibility from them
- make consequences ambiguous
- become the thing people blame

---

### 10. Phase Progression Does Not Relax Invariants

Later phases do not loosen rules.

Maturity does not permit:
- more automated judgment
- more hidden interpretation
- more silence
- more convenience at the cost of truth

## Phase I — Grounding

### Purpose

Phase I exists to establish **epistemic safety before construction**.

The goal is not to design a system, but to ensure that:
- authority is explicit
- boundaries are clear
- forbidden moves are named
- nothing implicit can later be mistaken for permission

If this phase is weak, later phases will encode assumptions as facts.

---

### Allowed Work

During Phase I, the project may:

- Define the **categories of things that may exist**  
  (not instances, not implementations)

- Define **who is allowed to recognize, declare, or refuse**  
  without defining workflows or tools

- Define **hard boundaries** between:
  - action and recognition
  - observation and judgment
  - recording and meaning

- Define **non-goals** and permanent exclusions

- Write constitutive language that says:
  “This system will never do X”

- Explicitly name **unknowns** and leave them unresolved

No behavior is automated in this phase.

---

### Forbidden Work

During Phase I, the project must not:

- Define features, screens, workflows, or user experiences
- Describe how anything will be implemented
- Encode success, failure, health, or quality
- Invent metrics, scores, rankings, or indicators
- Describe optimization, improvement, or efficiency
- Describe what “should” happen in response to conditions
- Collapse uncertainty into placeholders
- Use examples that imply future behavior

If something sounds useful, practical, or convenient, it is probably too early.

---

### Required Artifacts

To exit Phase I, the following must exist:

- A written definition of **what kinds of facts the system may record**
- A written definition of **what kinds of meaning the system must never assign**
- A clear statement of **who holds authority**, and where the system stops
- A durable list of **permanent exclusions**
- Explicit acknowledgment of **open questions** with no attempted resolution

All artifacts must be human-legible and non-technical.

---

### Exit Gate

Phase I may be exited only when a reviewer can say:

- “Nothing here pretends to know more than it does.”
- “No future behavior is implied by accident.”
- “If this were the only document left, misuse would still be hard.”

A lightweight adversarial audit is required.

If an auditor can point to:
- an implied feature
- an implied decision
- an implied judgment
- an implied authority

Then Phase I has failed and must be corrected before proceeding.

## Phase II — Representation

### Purpose

Phase II exists to allow the system to **represent reality without interpreting it**.

The goal is to:
- give durable form to what can be observed or declared
- make time, absence, and persistence visible
- do so without deciding what any of it means

This phase creates *containers*, not conclusions.

---

### Allowed Work

During Phase II, the project may:

- Define **representations of facts**, including:
  - events
  - declarations
  - absences
  - durations
  - sequences

- Define **distinctions between kinds of records**, such as:
  - actions versus acknowledgments
  - observations versus declarations
  - present statements versus historical records

- Define how **time is attached** to records
- Define how **absence is represented explicitly**
- Define how records are preserved without erasure
- Define how records may reference one another without collapsing roles

The system may now *hold* reality, but not *react* to it.

---

### Forbidden Work

During Phase II, the project must not:

- Attach meaning such as “good,” “bad,” “healthy,” or “concerning”
- Trigger actions based on recorded information
- Recommend responses or next steps
- Rank, score, or prioritize records
- Collapse multiple records into a single evaluative outcome
- Introduce automation that changes behavior elsewhere
- Imply causality, responsibility, or urgency

Representation must remain neutral, even when uncomfortable.

---

### Required Artifacts

To exit Phase II, the following must exist:

- A clear description of **each kind of record the system can hold**
- A clear description of **what each record explicitly does not mean**
- A description of how **time and persistence are preserved**
- A description of how **absence and silence are represented**
- A description of how records may be referenced without interpretation

All artifacts must avoid examples that imply action or judgment.

---

### Exit Gate

Phase II may be exited only when a reviewer can say:

- “These representations could be misused, but they do not encourage misuse.”
- “Nothing here tells a human what to think.”
- “Time, silence, and persistence are harder to ignore than to explain away.”

A lightweight adversarial audit is required.

If an auditor can extract:
- a recommendation
- a priority
- a judgment
- an implied response

Then Phase II has failed and must be corrected before proceeding.

## Phase III — Binding

### Purpose

Phase III exists to make reality **durable**.

The goal is to ensure that:
- what has occurred cannot be erased
- what has been acknowledged cannot be denied
- what has persisted cannot be normalized away

This phase binds memory, not meaning.

---

### Allowed Work

During Phase III, the project may:

- Declare which records are **append-only and irreversible**
- Define how new records may **supersede but never erase** prior records
- Define how **time-in-condition** is accumulated and preserved
- Define how **persistence remains visible**, regardless of familiarity
- Bind records to explicit moments of occurrence or recognition
- Bind records to explicit human authority where required

The system may now make forgetting structurally difficult.

---

### Forbidden Work

During Phase III, the project must not:

- Convert bound records into evaluations
- Decide whether persistence is acceptable
- Trigger alerts, actions, or escalations
- Encode thresholds, limits, or tolerances
- Collapse bound history into summaries that replace originals
- Introduce convenience mechanisms that weaken durability

Binding must increase discomfort when reality is inconvenient.

---

### Required Artifacts

To exit Phase III, the following must exist:

- A clear statement of **which records are irreversible**
- A clear description of **how correction works without erasure**
- A description of how **time accumulation is preserved**
- A description of how **continued non-change remains visible**
- A description of how **authority is bound to recognition where applicable**

All artifacts must emphasize preservation over usability.

---

### Exit Gate

Phase III may be exited only when a reviewer can say:

- “Nothing important can quietly disappear.”
- “Time passing makes reality clearer, not softer.”
- “Correction adds truth instead of replacing it.”

A lightweight adversarial audit is required.

If an auditor can demonstrate:
- silent overwrite
- hidden reset
- normalization through repetition
- erasure through convenience

Then Phase III has failed and must be corrected before proceeding.

## Phase IV — Exposure

### Purpose

Phase IV exists to make bound reality **legible to humans**.

The goal is to:
- surface what has been recorded and bound
- do so without collapsing, judging, or prescribing
- ensure humans can see persistence, absence, and time clearly

This phase exposes reality without explaining it.

---

### Allowed Work

During Phase IV, the project may:

- Define how bound records are **presented to humans**
- Define how **time, duration, and sequence** are made visible
- Define how **absence and silence** are shown explicitly
- Define how multiple records may be **viewed together without collapsing**
- Define how humans may **inspect original records and their history**
- Define how uncertainty is shown without resolution

The system may now show reality, but not interpret it.

---

### Forbidden Work

During Phase IV, the project must not:

- Rank, score, color-code, or label records by value or severity
- Provide summaries that replace original records
- Offer explanations, diagnoses, or narratives
- Suggest actions, priorities, or urgency
- Highlight “what matters most”
- Hide detail for the sake of clarity or comfort

Nothing shown may imply “this needs attention.”

---

### Required Artifacts

To exit Phase IV, the following must exist:

- A description of **how humans view bound records**
- A description of how **time and persistence are surfaced**
- A description of how **absence is unmistakable**
- A description of how **detail remains inspectable**
- A description of how **no interpretation is embedded in presentation**

All artifacts must be readable without specialized training.

---

### Exit Gate

Phase IV may be exited only when a reviewer can say:

- “What is shown is uncomfortable, but honest.”
- “Nothing here tells me what to think.”
- “If I ignore this, it is clearly my choice.”

A lightweight adversarial audit is required.

If an auditor can point to:
- visual judgment
- implied priority
- hidden aggregation
- softened persistence

Then Phase IV has failed and must be corrected before proceeding.

## Phase V — Reliance

### Purpose

Phase V exists to define the **conditions under which humans may rely on the system**
without surrendering judgment, authority, or responsibility.

The goal is not trust in the system,
but **trust in what the system refuses to do**.

Reliance is permitted only when misuse remains difficult.

---

### Allowed Work

During Phase V, the project may:

- Define the **explicit promises** the system makes to humans
- Define what the system is **safe to be relied upon for**
- Define what the system **must never be relied upon for**
- Define how reliance boundaries are **communicated clearly**
- Define how the system signals:
  - “this is complete”
  - “this is incomplete”
  - “this is absent”
  - “this is unresolved”

- Define how humans acknowledge reliance **explicitly**
- Define how responsibility remains human even when reliance occurs

The system may now be used with confidence—but never with abdication.

---

### Forbidden Work

During Phase V, the project must not:

- Encourage deference to the system’s judgment
- Present itself as authoritative or final
- Imply correctness, safety, or completeness by default
- Hide uncertainty once reliance is possible
- Collapse human responsibility into system behavior
- Allow reliance to become automatic or unconscious

The system must never say, explicitly or implicitly:
“you can stop thinking now.”

---

### Required Artifacts

To exit Phase V, the following must exist:

- A clear statement of **what reliance means**
- A clear statement of **where reliance stops**
- A clear description of **how uncertainty is still shown**
- A clear description of **how humans remain accountable**
- A clear description of **how misuse remains visible**

All artifacts must be understandable by non-specialists.

---

### Exit Gate

Phase V may be exited only when a reviewer can say:

- “I know exactly what this system will not do.”
- “If I misuse this, I cannot blame the system.”
- “Reliance here increases responsibility, not comfort.”

A lightweight adversarial audit is required.

If an auditor can demonstrate:
- authority creep
- implied correctness
- responsibility leakage
- hidden automation of judgment

Then Phase V has failed and must be corrected before completion.

## CONSTITUTIONAL AMENDMENT v2 — Tightening of Post-Reliance Phases VI–X

### Date
2026-01-24

### Author
Erik

### Sponsor
Erik

### Approver
Erik

### Recorded Adversarial Review
- planning/PROJECT_PHASE_CONSTITUTION_AMENDMENT_AUDIT.md

### Reason for Change

An adversarial review of the prior amendment defining Phases VI–X
identified several exploitable ambiguities that could permit:

- selective implementation of defined constraints,
- semantic fallback via “degraded operation,”
- implicit value judgments regarding abuse,
- selective erasure via survivorship definitions.

This amendment tightens language and adds explicit constraints to
eliminate those ambiguities **without expanding scope or authority**.

This is a corrective clarification amendment, not a structural redesign.

---

### Statement of Compatibility

This amendment:
- does not reopen or weaken Phases I–V,
- does not weaken any Global Invariant,
- preserves refusal rules and non-invention,
- preserves exposure as non-authoritative,
- preserves reports as the primary interface,
- strengthens auditability and constitutional enforceability.

If any conflict is discovered, this amendment is void.

---

### Full Prior Text (Being Replaced)

The following text is replaced **in full**:

> **Phase VI — Operability (Definition Only)**  
> **Phase VII — Abuse & Adversarial Resistance (Definition Only)**  
> **Phase VIII — Commercialization Boundaries (Definition Only)**  
> **Phase IX — Exit, Shutdown, and Irreversibility (Definition Only)**  
> **Phase X — Implementation (Execution)**  
>
> (As defined in the immediately preceding amendment.)

No other sections are modified.

---

### Full Replacement Text

---

#### Phase VI — Operability (Definition Only)

##### Purpose

Phase VI exists to define the **operability contract** of the system.

It specifies how the system is permitted to behave when:
- components fail,
- dependencies degrade,
- inputs are missing or malformed,
- capacity is exceeded,
- or the environment becomes unstable.

This phase defines constraints only.  
**No implementation is authorized.**

---

##### Allowed Work

During Phase VI, the project may **define and document**:

- classes of runtime failure,
- conditions under which operation must refuse,
- distinctions between:
  - operating,
  - reduced availability or capacity,
  - refusal,
  - unavailability,
- how failure, absence, silence, and uncertainty must remain visible,
- what “operational” explicitly does **not** imply.

Any description of reduced availability or capacity must not imply:
- reduced correctness requirements,
- reduced refusal obligations,
- continued fitness for purpose.

If defined guarantees cannot be met, **refusal is required**.

All outputs must be declarative and non-executable.

---

##### Forbidden Work

Phase VI must not:

- implement code, UI, or infrastructure,
- define recovery, retry, or self-healing,
- encode health, quality, or status judgments,
- optimize for uptime or resilience,
- suggest operator or user responses.

---

##### Required Artifacts

- Failure Mode Definition Catalog  
- Refusal Semantics Definition  
- Operational Non-Claims Statement  
- Phase VI Adversarial Audit Record  

---

##### Exit Gate

Phase VI may be exited only when a reviewer can say:

> “Operation here cannot be mistaken for correctness, safety, or success.”

---

#### Phase VII — Abuse & Adversarial Resistance (Definition Only)

##### Purpose

Phase VII exists to define how misuse, coercion, and adversarial behavior
are **made visible rather than prevented, moralized, or denied**.

This phase does not create guarantees.

---

##### Allowed Work

During Phase VII, the project may **define and document**:

- abuse and misuse scenarios,
- incentive and economic attack patterns,
- which abuse scenarios are surfaced explicitly,
- which abuse scenarios remain possible **without system-level visibility**, and
- explicit explanations for why visibility is not provided in those cases.

All distinctions must be descriptive, not evaluative.

---

##### Forbidden Work

Phase VII must not:

- promise prevention or safety,
- classify intent,
- enforce morality,
- suppress uncomfortable usage,
- implement controls or mitigations.

---

##### Required Artifacts

- Adversarial Misuse Catalog  
- Abuse Visibility Boundary (Surfaced vs Not Surfaced, with explanation)  
- Residual Harm Disclosure  
- Phase VII Adversarial Audit Record  

---

##### Exit Gate

Phase VII may be exited only when a reviewer can say:

> “If this is abused, the limits of visibility are explicit and not denied.”

---

#### Phase VIII — Commercialization Boundaries (Definition Only)

##### Purpose

Phase VIII exists to define what may be sold **without selling authority,
judgment, correctness, or protection**.

---

##### Allowed Work

During Phase VIII, the project may **define and document**:

- allowed marketing and sales claims,
- forbidden representations,
- contractual and warranty boundaries,
- demo behavior constraints.

---

##### Forbidden Work

Phase VIII must not:

- imply correctness, prediction, or safety,
- promise outcomes,
- collapse uncertainty for sales convenience,
- implement product behavior.

Demos must not display behavior, states, or language forbidden in the
production system.  
Any demo-specific simplifications must be **visibly disclosed within the demo itself**.

---

##### Required Artifacts

- Allowed Claims List  
- Forbidden Claims List  
- Sales & Marketing Language Constraints  
- Legal Representation Boundary  
- Phase VIII Adversarial Audit Record  

---

##### Exit Gate

Phase VIII may be exited only when a reviewer can say:

> “Nothing sold or demonstrated here implies the system knows or decides.”

---

#### Phase IX — Exit, Shutdown, and Irreversibility (Definition Only)

##### Purpose

Phase IX exists to ensure the system can be exited
**without erasing, rewriting, or softening reality**.

---

##### Allowed Work

During Phase IX, the project may **define and document**:

- shutdown semantics,
- customer exit paths,
- data export guarantees,
- post-shutdown data survivorship.

---

##### Forbidden Work

Phase IX must not:

- erase epistemic history,
- promise reputational cleanup,
- rewrite past records,
- implement exit tooling.

---

##### Required Artifacts

- Shutdown Protocol  
- Data Survivorship Map  
- Exit Disclosures  
- Irreversibility Acknowledgment  
- Phase IX Adversarial Audit Record  

**Binding Survivorship Constraint:**  
All records designated as binding or irreversible under Phase III
must survive export, shutdown, and post-operation retention.
No Phase III-bound record may be excluded by categorization or convenience.

---

##### Exit Gate

Phase IX may be exited only when a reviewer can say:

> “Stopping this system does not hide or revise reality.”

---

#### Phase X — Implementation (Execution)

##### Purpose

Phase X exists to authorize **construction** of the system strictly as a
realization of constraints defined in Phases VI–IX.

Implementation is permitted **only here**.

---

##### Allowed Work

During Phase X, the project may:

- implement code, UI, services, and infrastructure,
- implement refusal behavior **as specified** in Phase VI,
- implement abuse visibility **as specified** in Phase VII,
- enforce commercialization boundaries **as specified** in Phase VIII,
- implement exit and shutdown behavior **as specified** in Phase IX.

All implementation must be **explicitly traceable** to prior-phase artifacts.

---

##### Forbidden Work

Phase X must not:

- redefine meaning, authority, or boundaries,
- introduce new promises,
- encode judgment, scoring, or guidance,
- hide failures, absence, silence, or uncertainty,
- automate decision-making,
- implement behavior not defined in earlier phases.

Partial implementation of defined behavior is non-compliant.

---

##### Required Artifacts

- Implementation Trace Map (Phase VI–IX → components)
- **Coverage Verification Statement** affirming that all Phase VI–IX
  constraints are either:
  - fully implemented, or
  - explicitly unimplemented with justification and adversarial acknowledgment
- Phase X Adversarial Implementation Audit Record  

---

##### Exit Gate

Phase X may be exited only when a reviewer can say:

> “Everything defined was either implemented or explicitly accounted for,  
> and nothing built added authority.”

---

### Amendment Closure

This amendment tightens Phases VI–X to eliminate ambiguity while preserving
their original intent and scope.

Phases I–V remain closed and binding.

## CONSTITUTIONAL AMENDMENT v4 — Insertion of a Dedicated Guarantees Phase (Auditable and Refusal-Bound)

### Date
2026-01-26

### Author
Erik

### Sponsor
Erik

### Approver
Erik

### Recorded Adversarial Review
- planning/project phase constitution amendment audit 2.md

### Reason for Change

Prior versions of the Project Phase Constitution did not provide a dedicated, auditable location for defining what the system explicitly **guarantees** and explicitly **does not guarantee**.

As a result:
- guarantees risked being implied rather than declared,
- refusal semantics risked being uneven across phases,
- commercialization and reliance could invent claims post hoc,
- abuse-visibility work risked being conflated with promises of prevention.

This amendment introduces a **dedicated Guarantees phase** that is declarative only, refusal-bound, and explicitly inherits Phase VI refusal semantics, making over-claiming structurally difficult.

---

### Compatibility Statement

This amendment:
- does not weaken any Global Invariant,
- does not reduce refusal requirements,
- does not automate judgment or authority,
- does not bypass phase discipline,
- does not resolve tension through vagueness.

If any conflict with the Constitution is discovered, this amendment is void.

---

### Full Prior Text (Replaced in Full)

The following section of the Project Phase Constitution is replaced **in full**:

> **Phase VII — Abuse & Adversarial Resistance (Definition Only)**  
> **Phase VIII — Commercialization Boundaries (Definition Only)**  
> **Phase IX — Exit, Shutdown, and Irreversibility (Definition Only)**  
> **Phase X — Implementation (Execution)**  
>
> (As defined in Constitutional Amendment v2.)

No other constitutional text is modified.

---

### Full Replacement Text

---

#### Phase VII — Guarantees & Claim Boundaries (Definition Only)

##### Purpose

Phase VII exists to define **exactly what the system claims** and **exactly what it refuses to claim**.

No guarantee exists unless explicitly defined in this phase.

Silence outside the set of *considered claims* is meaningless; silence **within** the considered set is treated as explicit denial.

This phase does not implement guarantees.

---

##### Allowed Work

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

##### Forbidden Work

Phase VII must not:

- imply safety, prevention, or protection,
- soften guarantees through “best effort” or likelihood language,
- define mitigation, recovery, or retry behavior,
- define implementation mechanisms,
- introduce scoring, grading, or confidence labels.

If a guarantee cannot be enforced via refusal, it must not be claimed.

---

##### Required Artifacts

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

##### Refusal Semantics Inheritance

All refusals defined in Phase VII **must satisfy all Phase VI refusal invariants**.

Phase VII refusals are a **specialization of Phase VI refusals**, not a separate or weaker refusal system.

---

##### Exit Gate

Phase VII may be exited only when a reviewer can say:

> “Every claim considered by this project is either explicitly guaranteed, explicitly denied, or explicitly declared out of scope — and all guarantees are refusal-backed.”

---

---

#### Phase VIII — Abuse & Adversarial Resistance (Definition Only)

##### Purpose

Phase VIII exists to define how misuse, coercion, and adversarial behavior are **made visible or explicitly left unobserved**, without implying prevention or safety.

This phase does not create guarantees.

---

##### Allowed Work

During Phase VIII, the project may define and document:

- abuse and misuse scenarios,
- incentive and economic attack patterns,
- which abuse scenarios are surfaced explicitly,
- which abuse scenarios remain possible without system-level visibility,
- explicit explanations for why visibility is not provided.

All distinctions must be descriptive, not evaluative.

---

##### Forbidden Work

Phase VIII must not:

- promise prevention or safety,
- classify intent or morality,
- suppress uncomfortable usage,
- implement controls or mitigations.

Choosing not to surface abuse that **could be surfaced** requires explicit justification in the **Residual Harm Disclosure**.  
Convenience, cost, performance, or user preference are **not valid justifications**.

---

##### Required Artifacts

- Adversarial Misuse Catalog  
- Abuse Visibility Boundary  
- Residual Harm Disclosure  
- Phase VIII Adversarial Audit Record  

---

##### Exit Gate

Phase VIII may be exited only when a reviewer can say:

> “If this system is abused, the limits of visibility are explicit and not denied.”

---

---

#### Phase IX — Commercialization Boundaries (Definition Only)

##### Purpose

Phase IX defines constraints on how the system may be described, marketed, sold, demonstrated, or represented externally.

---

##### Required Artifacts

- Claim Consistency Check against Phase VII
- Prohibited Claim List
- Demonstration Constraint Statement

No commercial representation may introduce claims not present in Phase VII.

---

---

#### Phase X — Exit, Shutdown, and Irreversibility (Definition Only)

##### Purpose

Phase X defines irreversible actions and exit conditions, including shutdown semantics.

---

##### Required Artifacts

- Irreversibility Register
- Shutdown Disclosure Statement

No exit behavior may imply guarantees not defined in Phase VII.

---

---

#### Phase XI — Implementation (Execution)

##### Purpose

Phase XI authorizes implementation **only** as a realization of constraints defined in Phases VI–X.

---

##### Required Artifacts

- **Constraint Coverage Matrix**
  - Demonstrating that all constraints from Phases VI–X are:
    - realized, or
    - explicitly deferred with adversarial review

Selective implementation is forbidden.

---

### Impact Analysis (All Phases)

- **Phases I–V:** Unchanged.
- **Phase VI:** Unchanged; refusal and operability semantics preserved.
- **Phase VII:** New; introduces explicit, auditable claim discipline.
- **Phase VIII:** Clarified; prevents “chosen invisibility.”
- **Phases IX–X:** Strengthened through explicit linkage to guarantees.
- **Phase XI:** Coverage requirement added; no authority expansion.

---

### Renumbering Notice

All prior references to Phases VII–X are **void** and non-authoritative until updated to reflect this amendment.

---

### Amendment Closure

This amendment becomes authoritative only after:

- adversarial review records PASS,
- amendment is committed and tagged.

Until then, the prior phase structure remains in force.

---

### Closing Statement

This amendment exists to make **over-claiming detectable, auditable, and expensive**.

Guarantees are allowed —  
but only where refusal is stronger than promise.

## Phase Exit Audits (Adversarial, Human-Final)

### Purpose

Phase Exit Audits exist to prevent **self-certification**.

No phase may be exited solely by its authors.
Every phase must survive contact with an adversarial reader.

The audit protects the future from today’s confidence.

---

### Audit Requirements

At the end of each phase:

- A **human reviewer** must perform the audit
- The reviewer must not be the primary author of the phase
- The audit must be adversarial in posture, not collaborative
- The audit must be recorded durably

The auditor’s role is not to improve the work,  
but to try to **break its assumptions**.

---

### Audit Questions (Mandatory)

The auditor must attempt to answer:

- Where could this be misused?
- Where does this imply authority it does not name?
- Where does this suggest judgment without admitting it?
- Where does convenience override durability?
- Where could silence be mistaken for safety?

If any answer is non-empty, the phase does not pass.

---

### Audit Authority

Audit outcomes are binary:

- **Pass** — the phase may be exited
- **Fail** — the phase must be corrected

Conditional passes are not allowed.

---

## Refusals, Violations, and Invalid Work

### Mandatory Refusal

Any human or agent must refuse to act when:

- work violates a Global Invariant
- work exceeds the current phase’s allowed scope
- authority is unclear or missing
- a known fix is deferred in violation of the No Known Deferral rule
- a constitutional conflict exists

Refusal is not obstruction.  
Refusal is compliance.

---

### Invalid Work

Work is invalid if it:

- was performed in the wrong phase
- assumes permissions not explicitly granted
- encodes judgment implicitly
- hides absence, uncertainty, or persistence
- bypasses required artifacts or audits

Invalid work must be discarded, not patched.

---

### Violation Handling

When a violation occurs:

- it must be named explicitly
- it must be recorded durably
- it must be corrected within scope and authority if possible
- it must not be explained away

Repeated violations indicate structural failure, not individual failure.

---

## Amending This Constitution (Ceremony and Authority)

### Purpose

This section exists to ensure that change is **deliberate, visible, and costly**.

Ease of amendment is a failure mode.

---

### Amendment Preconditions

This Constitution may be amended only if:

- the proposed change is written in full
- the reason for change is stated plainly
- the impact on all phases is considered
- compatibility with the Constitution is explicitly affirmed

Amendments by implication are forbidden.

---

### Amendment Ceremony

Every amendment must include:

- the full prior text
- the full proposed replacement text
- a written justification
- a named human sponsor
- a named human approver
- a recorded adversarial review

Silent edits are invalid.

---

### Amendment Limits

This Constitution may not be amended to:

- weaken Global Invariants
- bypass phase discipline
- reduce refusal requirements
- automate judgment or authority
- resolve tension through vagueness

Any amendment that does so is void.

---

### Final Authority

If an amendment conflicts with the Constitution:

**The amendment is invalid.**

No exception process exists.

---

## Closing Statement

This Constitution exists to protect the project
from convenience, urgency, and hindsight.

If following this document feels slow,
that friction is intentional.

Speed is easy to add later.  
Integrity is not.
</code_selection>

</attached_files><user_query>
