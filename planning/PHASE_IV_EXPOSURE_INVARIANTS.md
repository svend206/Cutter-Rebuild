---
doc_id: phase_iv_exposure_invariants
doc_type: spec
status: active
version: 1.0
date: 2026-01-23
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/PROJECT_PHASE_CONSTITUTION.md, planning/PHASE_IV_WORK_CHARTER.md]
conflicts_with: []
tags: [phase, exposure, invariants, spec]
---

# Phase IV — Exposure Invariants

Phase: IV — Exposure  
Status: Draft (Intent-Locked)

---

## Purpose

These invariants define what exposure **must not violate**.

They exist to ensure that making reality visible to humans does not:
- introduce judgment,
- imply authority,
- collapse history,
- or convert silence into reassurance.

Any exposure that violates these invariants is invalid, regardless of usefulness or intent.

---

## 1. Visibility Invariants

- Every bound record type must be exposable to humans.
- No record may become invisible due to default filtering, summarization, or convenience.
- Visibility must not depend on interpretation, thresholds, or “relevance.”
- If a record exists, it must be possible for a human to find and inspect it.

Exposure may reduce *how much* is shown at once, but never *what exists*.

---

## 2. Absence and Silence Invariants

- Absence and non-occurrence must be shown explicitly.
- Silence must never be rendered as:
  - success
  - safety
  - normality
  - resolution

- Any view that omits expected activity must indicate that omission clearly.
- “No data” must not be visually indistinguishable from “nothing happened.”

No exposure may rely on the assumption that missing information is benign.

---

## 3. History and Supersession Invariants

- Prior records must remain inspectable even after supersession.
- Supersession must not:
  - erase history
  - hide earlier declarations
  - imply correctness of newer records

- Exposure must not present a single “current truth” without making history accessible.
- If a record has been superseded, that fact must be visible without obscuring the original.

History must resist collapse.

---

## 4. Reduction and Reversibility Invariants

- Reduction (grouping, paging, folding, summarizing) is allowed only if:
  - it is explicit
  - it is reversible
  - the underlying records remain accessible

- Any reduced view must:
  - indicate that reduction has occurred
  - provide a clear path to inspect originals

Reduction must never be silent or irreversible.

---

## 5. Non-Authority Invariants

Exposure must not imply judgment or instruction.

Specifically forbidden:

- Color, ordering, or emphasis implying:
  - health
  - priority
  - urgency
  - success or failure

- Labels such as:
  - “good”
  - “bad”
  - “normal”
  - “problem”
  - “resolved”

- Defaults that imply correctness or recommended focus.

If exposure causes a human to feel told what to think or do, it has violated this invariant.

---

## 6. Deferred Risk Resolution Constraints

Phase III explicitly deferred the following risks to Phase IV.  
Phase IV may address them only within the bounds below.

### 6.1 Record Volume and Obscuring

- Exposure must prevent large volumes of records from hiding individual records.
- Mitigation may include:
  - explicit grouping
  - explicit paging
  - explicit narrowing chosen by the human

- Mitigation must not include:
  - silent filtering
  - ranking by importance
  - suppression of records

Volume reduction must be visible and reversible.

---

### 6.2 Human Inspectability and Accessibility

- Exposure must ensure records remain practically inspectable by humans.
- Inspectability must not require:
  - specialized tools
  - reconstruction
  - expert intervention

- Loss of practical inspectability is treated as loss of visibility.

Exposure must favor accessibility over efficiency.

---

## 7. Invariant Enforcement

- Any exposure design that violates these invariants must be refused.
- Usefulness, clarity, or user preference do not override invariants.
- Violations are structural failures, not design tradeoffs.

---

## Closing Statement

These invariants exist to protect humans from being quietly guided,
reassured, or misled by exposure.

If an exposure feels calming, decisive, or resolving,
it is likely wrong.
