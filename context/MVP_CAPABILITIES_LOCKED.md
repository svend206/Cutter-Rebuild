---
doc_id: mvp_capabilities_locked
doc_type: context
status: active
version: 2.0
date: 2026-01-21
owner: Erik
authoring_agent: architect
supersedes: [version 1.0]
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [mvp, capability, locked, context]
---

# MVP — Locked Capability Definition

**Status:** LOCKED

This document defines the locked Minimum Viable Product (MVP) for the system.
The MVP is expressed strictly as **capabilities**, not features, modules, UX designs, defaults, workflows, or plans.

The purpose of this MVP is to establish an **irreversible epistemic core**:
preservation of demonstrated reality, explicit human authority, cognitive discipline under pressure, continuous execution, non-blocking reconciliation, and refusal of automated harm.

---

## MVP-1 — Ops can perform work and emit exhaust

**Capability**  
The system can allow a user to perform operational actions while emitting immutable operational exhaust for each action.

**Success condition**  
For any permitted operational action, a corresponding exhaust record exists that includes actor identity, timestamp, and action-relevant values, and that record cannot be altered or deleted.

---

## MVP-2 — Cutter Ledger preserves demonstrated operational reality

**Capability**  
The system can append and retain operational exhaust in an immutable ledger that preserves sequence, frequency, and duration without summarization, smoothing, normalization, or interpretation.

**Success condition**  
Given repeated or sustained operational variance, the Cutter Ledger shows each occurrence and its time persistence intact, without collapse, aggregation, or overwrite of prior records.

---

## MVP-3 — Cutter Ledger is read-only with respect to meaning

**Capability**  
The system can present Cutter Ledger records without assigning judgment, status, severity, health, priority, or domain meaning.

**Success condition**  
Ledger records are viewable chronologically with values and timestamps only, and no UI surface, data field, derived attribute, or computation encodes evaluation, recommendation, or interpretation.

---

## MVP-4 — State Ledger supports explicit human recognition

**Capability**  
The system can record explicit, present-tense state declarations made by a single named recognition owner for a defined entity.

**Success condition**  
A state entry exists only when a human submits it explicitly, includes recognition owner identity and timestamp, and never appears, updates, or expires without a human action.

---

## MVP-5 — State continuity requires explicit reaffirmation

**Capability**  
The system can preserve prior state declarations and accumulate time-in-state unless a new reaffirmation or reclassification is explicitly recorded.

**Success condition**  
If no reaffirmation or reclassification is entered, the prior state remains visible with increasing time-in-state, and silence does not create a new record, reset time, or imply continuity.

---

## MVP-6 — Evidence may be referenced but never evaluated

**Capability**  
The system can allow a state declaration to optionally reference specific Cutter Ledger records or Ops artifacts as evidence, without any system interpretation, validation, scoring, or evaluation.

**Success condition**  
Referenced evidence is stored as inert, non-binding metadata for human auditability only, and the system performs no logic based on the presence, absence, or content of referenced evidence.

---

## MVP-7 — Separation between Ops, Cutter Ledger, and State Ledger is enforced

**Capability**  
The system can prevent Ops from declaring state, prevent ledgers from triggering action, and prevent any inference, automation, or automatic transition between layers.

**Success condition**  
No state entry is created from Ops behavior alone, no Ops workflow changes based on ledger contents, and no automatic classification, escalation, recommendation, or gating appears anywhere in the system.

---

## MVP-8 — Explicit, downstream-only Guild exhaust export

**Capability**  
The system can export selected operational exhaust to the Guild as raw, additive records, initiated only by explicit human action, with no feedback into Ops, Cutter Ledger, or State Ledger.

**Success condition**  
Exported records preserve provenance and immutability, appear only within the Guild context, and produce no operational, ledger, or state-side effects.

---

## MVP-9 — System authority is document-governed and non-inventive

**Capability**  
The system can operate without relying on undocumented assumptions, inferred rules, defaults, or non-authoritative context documents.

**Success condition**  
All enforced constraints trace to constitution, spec, or decision log documents listed in `DIRECTORY.md`, and ignoring context documents does not change system behavior.

---

## MVP-10 — Absence of action is a preserved, inspectable fact

**Capability**  
The system can make the absence of expected or possible actions visible through preserved time, without inferring intent, failure, health, priority, or state.

**Success condition**  
For any entity, operation, or state context, elapsed time without a corresponding action remains visible and durable, cannot be collapsed or hidden, and is not converted into judgments, alerts, or automated conclusions.

---

## MVP-11 — Ops enforces separation of execution and planning modes

**Capability**  
The system can enforce an explicit separation between execution mode and planning mode in the Ops layer, such that execution mode suppresses aggregation, interpretation, reassurance, metrics, dashboards, guidance, and optimization, while planning mode permits reflective analysis on pinned reality.

**Success condition**  
While in execution mode, only immediately actionable information is available and no planning-only signals appear; mode transitions are explicit, intentional, and auditable.

---

## MVP-12 — Reconciliation is explicit, query-dependent, and non-blocking

**Capability**  
The system can support explicit human reconciliation that is relative to a specific question or report, is not global, does not imply completion or finality, and does not block ongoing execution or exhaust emission.

**Success condition**  
A reconciliation can exist for a given report or scope while execution continues uninterrupted, and no global “reconciled state” is created or required.

---

## MVP-13 — Execution is continuous and never gated

**Capability**  
The system can allow operational work and exhaust emission to proceed continuously, regardless of reconciliation status, planning activity, or incomplete information.

**Success condition**  
No reconciliation, report, or analysis state prevents or delays Ops actions or exhaust creation.

---

## MVP-14 — Exhaust capture is a byproduct, not an obligation

**Capability**  
The system can record operational facts as a byproduct of work without requiring explanations, justifications, reason codes, or annotations during execution.

**Success condition**  
An operator can complete execution flows without providing explanatory input, and omissions remain visible rather than blocked or inferred.

---

## MVP-15 — The system explicitly refuses automated harm and blame computation

**Capability**  
The system can explicitly refuse to compute, retain, or present views that automate, scale, or normalize individual blame, performance scoring, or normative judgment.

**Success condition**  
When such queries or views are attempted, the system responds with an explicit refusal rather than silent omission or deferred implementation.

---

## Lock Statement

This MVP definition is **locked**.

- No additional capabilities may be added without an explicit unlock.
- Capabilities may not be weakened, reinterpreted, or partially satisfied.
- Features, modules, UX layouts, defaults, and plans are intentionally excluded.

This document exists to enable objective comparison to current reality, precise gap identification, disciplined verification, and execution without scope drift.
