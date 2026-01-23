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
