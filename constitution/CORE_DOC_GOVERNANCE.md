---
doc_id: core_doc_governance
doc_type: constitution
status: locked
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [governance, documents]
---

# Document Governance Constitution

## Intent
Prevent epistemic drift caused by document entropy.

This constitution defines:
- what kinds of documents may exist
- where authority lives
- how documents may evolve
- how AI agents must behave when creating or modifying documents

This document governs **structure and authority**, not product behavior.

---

## Scope
This constitution applies to:
- all markdown and text documents in this repository
- all AI agents (Cursor, ChatGPT, others)
- all future documentation work

It does **not** govern:
- application code
- database contents
- UI behavior
- business decisions

---

## Non-Goals
This constitution does not:
- define product features
- specify algorithms or workflows
- optimize developer productivity
- enforce stylistic consistency

Its sole concern is **truth preservation**.

---

## Load-Bearing Constraints

### C1. Every Document Has Exactly One Class
Every document MUST belong to exactly one of the following classes:
1. **constitution**
2. **decision_log**
3. **spec**
4. **context**
5. **archive**

No hybrid documents are permitted.

---

### C2. Authority by Class
| Class | Authority | Mutability | Load Order |
|-----|----------|------------|-----------|
| constitution | Highest | Rare, explicit | 1 |
| decision_log | Binding | Append-only | 2 |
| spec | Executable | Rewrite allowed | 3 |
| context | None | Free | Excluded |
| archive | None | Read-only | Never |

Only **constitution**, **decision_log**, and **spec** may influence system behavior.

---

### C3. CONTEXT Is Explicitly Non-Authoritative
CONTEXT documents:
- may explain rationale, workflow, or philosophy
- may not introduce rules, constraints, or invariants
- may not be cited as upstream authority
- must be safe to ignore without changing system behavior

If ignoring a document would change a correct implementation, that document is **misclassified**.

---

### C4. Mandatory Machine-Readable Header
All non-archived documents MUST begin with a YAML header containing:
- doc_id
- doc_type
- status
- version
- date
- owner
- authoring_agent
- supersedes
- superseded_by
- authoritative_sources
- conflicts_with
- tags

Documents without this header are **invalid** until corrected.

---

### C5. DIRECTORY.md Is the Sole Registry
`DIRECTORY.md` is the single source of truth for:
- what documents are authoritative
- where they live
- what order they load in

If a document is not listed in `DIRECTORY.md`, it has **no authority**, regardless of its content.

---

### C6. Supersession Must Be Explicit
No document may silently override another.

Supersession requires:
- explicit `supersedes` metadata
- update to `DIRECTORY.md`
- preservation of the superseded document

---

### C7. AI Enforcement Rules (Hard)
AI agents MUST:
1. classify a document before creating it
2. check `DIRECTORY.md` for overlap
3. refuse to invent doctrine
4. ask before altering meaning
5. update `DIRECTORY.md` when structure changes

AI agents MUST NOT:
- reinterpret constitutions
- infer authority from tone or filename
- merge documents without instruction
- create shadow rulebooks

---

## Change Control
This constitution may be changed only by:
- explicit owner instruction
- new decision log entry
- version increment
- preserved prior versions

Silence does not constitute approval.

---

## Closing Statement
Document structure **is** system structure.

If authority is unclear, the system is already failing.

This constitution exists to make that failure impossible to hide.
