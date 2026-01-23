---
doc_id: report_phase_i_adversarial_tests_20260123_113450
doc_type: context
status: active
version: 1.2
date: 2026-01-23
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/PROJECT_PHASE_CONSTITUTION.md, planning/Phase_I_work_charter.md]
conflicts_with: []
tags: [report, phase, adversarial, tests, context]
---

# REPORT 35 — PHASE I ADVERSARIAL TESTS

## Scope
Targets Phase I governance documents:
- `boot/PROJECT_PHASE_CONSTITUTION.md`
- `planning/Phase_I_work_charter.md`

Purpose: address the adversarial attack vectors by defining tests and recording results.

---

## Test Suite

### T1 — Category Naming Does Not Smuggle Structure
**Attack addressed:** Naming categories implies schema.  
**Method:** Inspect Phase I docs for category naming that enumerates fields, attributes, or record structure.  
**Pass criteria:** Categories are named without field lists, schemas, or behaviors.  
**Result:** PASS — Category naming is bounded by “not instances, not implementations” and “without defining structure or behavior.”

### T2 — Boundary Definitions Stay Abstract
**Attack addressed:** “Hard boundary” definitions smuggle record contents.  
**Method:** Inspect boundary definitions for any lists of record contents, fields, or data attributes.  
**Pass criteria:** Boundaries are conceptual only, no field/content enumerations.  
**Result:** PASS — Boundaries are stated as conceptual separations only.

### T3 — Permanent Exclusions Do Not Invert into Feature Lists
**Attack addressed:** Exclusions imply features by negation.  
**Method:** Inspect exclusions for any inverse claims that imply schema or features (e.g., “never rank quotes by profitability”).  
**Pass criteria:** Exclusions remain high‑level and do not enumerate implied fields or entity types.  
**Result:** PASS — No exclusion list enumerates implied data structures or features.

### T4 — Unknowns Are Framed Without Hidden Commitments
**Attack addressed:** Unknowns framed as forced design decisions.  
**Method:** Inspect “unknowns” language for embedded structural assumptions.  
**Pass criteria:** Unknowns are stated without assuming concrete entities, fields, or relationships.  
**Result:** PASS — Unknowns remain general and do not pre‑commit to schema.

### T5 — Authority Statements Avoid New Entity Models
**Attack addressed:** Authority language smuggles “entity/state/classification.”  
**Method:** Inspect authority statements for implicit entity model or hierarchy.  
**Pass criteria:** Authority described in abstract terms without introducing new entity types.  
**Result:** PASS — Authority boundaries are stated without new domain entities.

### T6 — Constitutional Language Is Not Laundered into Design
**Attack addressed:** Constitution terms used to justify proto‑schema.  
**Method:** Inspect for lists of “values, deltas, timestamps” presented as implementation scaffolding.  
**Pass criteria:** Constitutional terms are not converted into Phase I record designs.  
**Result:** PASS — No conversion into record schemas appears.

### T7 — Plain‑Language Descriptions Do Not Become Feature Specs
**Attack addressed:** Non‑technical prose used as spec.  
**Method:** Inspect for narrative statements that describe system behaviors or flows.  
**Pass criteria:** No prose specifies behaviors, flows, or feature outcomes.  
**Result:** PASS — No behavioral narratives present.

### T8 — Authority Chain Preserved (Charter Cannot Loosen Constitution)
**Attack addressed:** Charter omission used to weaken constraints.  
**Method:** Verify Work Charter language retains the Phase I restriction against instances/implementations.  
**Pass criteria:** Charter contains explicit “no structure/behavior” constraints aligned to Constitution.  
**Result:** PASS — Work Charter includes “without defining their structure or behavior.”

### T9 — Required Outputs Do Not Enumerate Knowledge Fields
**Attack addressed:** “Allowed to know” becomes proto‑schema.  
**Method:** Inspect required outputs for explicit lists of fields or record types.  
**Pass criteria:** Required outputs are abstract statements, not enumerated data fields.  
**Result:** PASS — Required outputs remain abstract.

### T10 — Open Questions Do Not Presuppose Structure
**Attack addressed:** Questions pre‑commit to relationships or records.  
**Method:** Inspect open‑question language for implied entities/relations.  
**Pass criteria:** No open questions introduce schema assumptions.  
**Result:** PASS — Open questions remain abstract.

---

## Human Tests Required

### H1 — Phase I Artifact Review (Per New Document)
**When:** Every time a new Phase I artifact is proposed.  
**How:**  
1) Read the artifact line‑by‑line.  
2) Flag any sentence that lists data fields, record attributes, or behaviors.  
3) Ask: “Could this be implemented directly as a schema or workflow?”  
4) If yes, mark as phase violation and require revision.  
**Pass condition:** No sentence can be interpreted as a data model or behavior spec.

### H2 — Negation Leak Check
**When:** Any “never do X” or exclusion list is added.  
**How:**  
1) Invert each exclusion into its implied capability.  
2) If the inversion would define a record, entity, or workflow, the exclusion is too specific.  
3) Require rewrite to a higher‑level exclusion.  
**Pass condition:** Inversions do not imply schema or workflow.

### H3 — Unknowns Framing Check
**When:** Open questions are written.  
**How:**  
1) Identify nouns in each question.  
2) If nouns imply record types or relationships, reframe to a higher‑level question.  
**Pass condition:** Questions do not presuppose data structures.

---

## Summary
All automated document‑inspection tests pass.  
Three human‑judgment tests are required for any new Phase I artifacts to prevent smuggled design through prose.

---

## Addendum — 2026-01-23 Phase II Language Fixes

Scope: language-only edits to Phase II artifacts to remove implied agency, workflow, and evaluation.

### Record Types Catalogue (planning/PHASE_II_RECORD_TYPES_CATALOG.md)
- “Hold a durable statement that the system refused to act.” → “Hold a durable statement that a refusal occurred and an attempted action was not performed.”
- “That a refusal occurred and was recorded.” → “That a refusal occurred and was recorded, including its stated reason.”
- “Hold a durable statement that a newer record corrects or supersedes a prior record.” → “Hold a durable statement that one record is designated as superseding another.”
- “That a correction or supersession was recorded without erasing history.” → “That a supersession designation was recorded without erasing history.”
- “That the earlier record was careless, invalid, or blameworthy.” → “That the earlier record was erroneous, careless, invalid, or blameworthy.”

### Representation Invariants (planning/PHASE_II_REPRESENTATION_INVARIANTS.md)
- “Records must preserve when they occurred or were declared.” → “Records include when they occurred or were declared.”
- “Records may refer to other records only as “refers to.”” → “Reference relationships between records are representable only as “refers to.””
- “Each record stands on its own terms.” → “Each record is preserved independently.”

### Phase II Work Charter (planning/PHASE_II_WORK_CHARTER.md)
- “Defining how time attaches to records” → “Defining how time is represented as part of each record”
- “Defining how records may reference each other without collapsing roles” → “Defining how reference relationships between records are representable without collapsing roles”
