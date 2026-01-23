---
doc_id: phase_iii_work_charter
doc_type: spec
status: active
version: 1.0
date: 2026-01-23
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [boot/PROJECT_PHASE_CONSTITUTION.md]
conflicts_with: []
tags: [phase, binding, charter, spec]
---

# Phase III — Work Charter (Binding)

Phase: III — Binding

Status: Active

---

## Intent

Phase III exists to make selected records **durable, ordered, and irreversible**.

The goal is to ensure that:
- reality cannot be rewritten,
- silence cannot be erased,
- refusals cannot be softened,
- and history cannot be edited for convenience.

This phase binds representation to permanence without assigning meaning.

---

## Allowed Work (This Phase Only)

During Phase III, work may include:

- Declaring which record types are **append-only**
- Declaring which records are **irreversible once written**
- Declaring how **ordering** between records is preserved
- Declaring how **supersession** works without deletion
- Declaring durability rules for:
  - actions
  - observations
  - declarations
  - refusals
  - absence records

- Declaring what **cannot be altered, merged, or compacted**
- Declaring what must remain **inspectable forever**

All declarations must be descriptive and constraint-based.

---

## Forbidden Work

During Phase III, the project must not:

- Introduce interpretation, scoring, or evaluation
- Introduce automation or closed-loop behavior
- Define responses, alerts, or actions
- Define user interfaces or experiences
- Optimize storage, performance, or cost
- Allow any record to be silently rewritten or erased

If a rule makes something easier to manage but weaker to audit, it is forbidden.

---

## Required Outputs (to Exit Phase III)

Before Phase III can end, the following must exist:

- A binding declaration for each record type stating:
  - whether it is append-only
  - whether it is irreversible
  - whether it may be superseded (and how)

- A clear statement of **what history can never change**
- A clear statement of **what corrections cannot erase**
- A clear statement of **what silence must remain visible**
- A clear statement of **what refusal must remain durable**

---

## Known Unknowns (Intentionally Preserved)

The following are explicitly not resolved in Phase III:

- How records are stored
- How records are queried
- How records are presented to humans
- How records influence decisions
- How long records are retained (beyond irreversibility)

These belong to later phases.

---

## Exit Condition (Human Judgment)

Phase III ends only when a reviewer can say:

- “Nothing important can be quietly rewritten.”
- “History resists convenience.”
- “Accountability survives optimization.”

A lightweight adversarial audit is required.
