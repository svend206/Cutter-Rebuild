---
doc_id: clean_rebuild_execution_plan
doc_type: spec
status: active
version: 1.1
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [rebuild, governance, bootstrap]
---

# CLEAN REBUILD EXECUTION PLAN
*(Pre-Scaffold Reset → Minimal Governance Core)*

## Purpose
Rebuild the project from a clean root using a **minimal, internally consistent governance set**:
- Boot Contract
- Constitution
- Integrator Home
- Inbox
- Architecture Memory
- Bootstrap Pack

This plan assumes:
- Existing artifacts may be reused selectively
- No attempt will be made to “fix” the old system in place
- Authority, clarity, and restart determinism are the primary goals

## Decision (Option 1 Selected)
Create a **new root folder outside the existing repo**. The old repo remains intact and is accessed only for selective promotion. No history reset is required.

## Authority Clarification
- **Constitution is highest authority.**
- **Boot Contract is operational and may not override Constitution.**

---

## PHASE 0 — SAFETY & BASELINE

### 0.1 Preserve the old world
- [ ] Keep the existing repo intact (no reset, no deletion)
- [ ] Ensure it remains a stable reference for promotion

### 0.2 Pre-scaffold rollback (N/A for Option 1)
- [ ] Not applicable when using a separate root outside git history

---

## PHASE 1 — CREATE A CLEAN ROOT (NO LOGIC YET)

### 1.1 Create a new top-level root
- [x] Create a new root folder (outside the old repo)
- [ ] Treat this as the **only authoritative workspace going forward**
- [ ] Old files remain outside this root unless explicitly promoted

### 1.2 Create the empty skeleton
- [x] `/boot/`
- [x] `/constitution/`
- [x] `/integrator/`
- [x] `/inbox/`
- [x] `/architecture/`
- [x] `/bootstrap/`
- [x] `/archive/` (optional, for deprecated artifacts)

No content yet. Structure only.

---

## PHASE 2 — BOOT CONTRACT (GATE TO ACTION)

### 2.1 Create the Boot Contract
- [ ] Create `/boot/BOOT_CONTRACT.md`
- [ ] Keep it **short and declarative**
- [ ] No workflow, no process, no tasks

### 2.2 Boot Contract must explicitly state
- [ ] What documents are authoritative
- [ ] What agents may **not** invent or assume
- [ ] Where current operational truth lives
- [ ] What happens if the contract is not acknowledged (refusal to act)

### 2.3 Validate scope
- [ ] Applies to humans, Cursor, and external AI equally
- [ ] No reference to scaffolding, intake, or amendment systems

---

## PHASE 3 — CONSTITUTION (LAW ONLY)

### 3.1 Create Constitution folder
- [ ] `/constitution/` contains **only invariants**
- [ ] Each file answers exactly **one** rule or principle

### 3.2 Promote only proven law
For each existing doctrine you consider reusing:
- [ ] Ask: “Is this always true, or was it process?”
- [ ] If always true → candidate for Constitution
- [ ] If procedural → reject or move elsewhere

### 3.3 Constitution rules
- [ ] No status
- [ ] No tasks
- [ ] No phases
- [ ] No workflow instructions
- [ ] No references to ‘current work’

If it can change next week, it does not belong here.

---

## PHASE 4 — INTEGRATOR HOME (SINGLE STATUS SURFACE)

### 4.1 Create Integrator Home
- [ ] Create `/integrator/INTEGRATOR_HOME.md`
- [ ] This is the **only** place that answers “what are we doing?”

### 4.2 Required sections
- [ ] Current task(s) (cap at 3)
- [ ] Next task(s)
- [ ] Recently completed (short list)

### 4.3 Explicit exclusions
- [ ] No ideas
- [ ] No backlog
- [ ] No architecture
- [ ] No discussion
- [ ] No historical narrative

If it’s not active or next, it does not go here.

---

## PHASE 5 — INBOX (CAPTURE WITHOUT THINKING)

### 5.1 Create Inbox
- [ ] Create `/inbox/INBOX.md`
- [ ] Treat as **append-only during capture**

### 5.2 Inbox rules
- [ ] No prioritization on capture
- [ ] No decisions on capture
- [ ] Items have **no authority** until promoted

### 5.3 Drain discipline
- [ ] Periodically move items to:
  - Integrator Home (if active work)
  - Architecture (if structural memory)
  - Archive (if resolved or rejected)

---

## PHASE 6 — ARCHITECTURE MEMORY (WHAT EXISTS)

### 6.1 Create Architecture folder
- [ ] `/architecture/` holds descriptive system memory
- [ ] Focus on **what exists**, not what should exist

### 6.2 Candidate contents
- [ ] Modules
- [ ] Features
- [ ] Data models
- [ ] Key design decisions (non-constitutional)

### 6.3 Promotion rule
- [ ] Architecture files may reference Constitution
- [ ] Constitution must never reference Architecture

Law flows downward only.

---

## PHASE 7 — BOOTSTRAP PACK (DETERMINISTIC RESTART)

### 7.1 Create Bootstrap Pack
- [ ] Create `/bootstrap/`
- [ ] This is the **only** folder loaded to start a new chat

### 7.2 Required contents
- [ ] Boot Contract (authoritative at `/boot/BOOT_CONTRACT.md`)
- [ ] Pointer/index to Constitution
- [ ] Integrator Home
- [ ] Short “How to start a session” note

### 7.3 Hard rule
- [ ] If it is not in the Bootstrap Pack, agents must not assume it exists

This replaces all scaffold ceremony.

---

## PHASE 8 — CURSOR-FIRST REBUILD

### 8.1 Use Cursor intentionally
- [ ] Point Cursor only at the new root
- [ ] Do not let Cursor “clean up” old artifacts
- [ ] Reintroduce legacy files **only by promotion**

### 8.2 Promotion test for old artifacts
For each file considered:
- [ ] Does it have a single clear role?
- [ ] Does it conflict with any new artifact?
- [ ] Can it be rewritten smaller with what you now know?

If not, archive it.

---

## PHASE 9 — CONSISTENCY CHECK

### 9.1 Verify no overlaps
- [ ] Only one status surface exists
- [ ] Only one boot contract exists
- [ ] Constitution contains no mutable content

### 9.2 Verify restart determinism
- [ ] A new chat can be started using only `/bootstrap/`
- [ ] No hidden assumptions are required

---

## DONE CRITERIA

The rebuild is complete when:
- [ ] You can explain the system to a new agent in under 2 minutes
- [ ] There is no duplicated authority
- [ ] Nothing important depends on chat memory
- [ ] You feel relief, not fragility, opening the repo

---

## FINAL NOTE

This rebuild is not about deleting “bad work.”
It is about **respecting what you now understand**.

Clean roots are not waste.
They are how real systems mature.
