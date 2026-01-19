---
doc_id: mvp_capability_definition
doc_type: spec
status: active
version: 1.0
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [mvp, capability, planning]
---

# MVP — Capability Definition

This document defines the Minimum Viable Product (MVP) for the system. The MVP is expressed strictly as *capabilities*, not features, modules, UX designs, or plans. Any system behavior not covered here is explicitly out of scope for MVP evaluation.

The purpose of this MVP is to establish an irreversible epistemic core: preservation of demonstrated reality, explicit human authority, cognitive discipline under pressure, and strict separation between operation, truth, recognition, planning, execution, and market intelligence.

---

## MVP-1 — Ops can perform work and emit exhaust

**Capability**
The system can allow a user to perform operational actions while emitting immutable operational exhaust for each action.

**Success condition**
For any permitted operational action, a corresponding exhaust record exists that includes actor identity, timestamp, and action-relevant values, and that record cannot be altered or deleted.

---

## MVP-2 — Cutter Ledger preserves demonstrated operational reality

**Capability**
The system can append and retain operational exhaust in an immutable ledger that preserves sequence, frequency, and duration without summarization, smoothing, or interpretation.

**Success condition**
Given repeated or sustained operational variance, the Cutter Ledger shows each occurrence and its time persistence intact, without collapse, normalization, or overwrite of prior records.

---

## MVP-3 — Cutter Ledger is read-only with respect to meaning

**Capability**
The system can present Cutter Ledger records without assigning judgment, status, severity, health, priority, or domain meaning.

**Success condition**
Ledger records are viewable chronologically with values and timestamps only, and no UI surface, data field, or derived attribute encodes evaluation, recommendation, or interpretation.

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
No state entry is created from Ops behavior alone, no Ops workflow changes based on ledger contents, and no automatic classification, escalation, or recommendation appears anywhere in the system.

---

## MVP-8 — Explicit, downstream-only Guild exhaust export

**Capability**
The system can export selected operational exhaust to the Guild as raw, additive records, initiated only by explicit human action, with no feedback into Ops, Cutter Ledger, or State Ledger.

**Success condition**
Exported records preserve provenance and immutability, appear only within the Guild context, and produce no operational, ledger, or state-side effects.

---

## MVP-9 — System authority is document-governed and non-inventive

**Capability**
The system can operate without relying on undocumented assumptions, inferred rules, or non-authoritative context documents.

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
The system can enforce an explicit separation between execution mode and planning mode in the Ops layer, such that execution mode suppresses aggregation, pattern recognition, interpretation, metrics, dashboards, guidance, and optimization, while planning mode permits reflective analysis, aggregation, and interpretation, without allowing accidental or implicit mode mixing.

**Success condition**
When the system is in execution mode, only immediately actionable information is available and no planning-only signals can be surfaced; when in planning mode, analytical and historical views are available, and mode switching is explicit, intentional, and auditable.

---

This document exists to enable objective comparison to current reality, precise gap identification, and disciplined execution without scope drift.
