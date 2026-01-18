---
doc_id: core_query_layer_rules
doc_type: constitution
status: locked
version: 1.1
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [query, rules]
---

# Query Layer Rules (Constitutional)

## Purpose
The Query Layer defines how preserved operational reality may be *accessed, sliced, and presented* without assigning meaning.

Queries are an **epistemic boundary**.
They may support human perception.
They must never perform human judgment.

---

## Core Principle
> **The query layer may structure perception, but must never structure interpretation.**

Any query behavior that assigns importance, severity, causality, or recommended action violates this constitution.

---

## Allowed Query Operations
The query layer MAY:
- Read from Ops, Cutter Ledger, and State Ledger in a strictly read-only manner
- Filter by explicit predicates chosen by a human
- Slice by time range, subject, actor, or scope
- Preserve full temporal ordering of events
- Display literal values, timestamps, and provenance
- Compute mechanical predicates *explicitly specified by the user*
- Present aggregates **only when the underlying instance set is directly accessible**

Examples of allowed predicates:
- `actual_time > promised_time`
- `event_type == X`
- `timestamp within range R`

The query layer may never invent predicates.

---

## Forbidden Query Operations
The query layer MUST NOT:
- Rank results by importance or priority
- Score, grade, or label health or severity
- Highlight "top" items
- Suppress or hide underlying instances
- Assign causality or explanation
- Recommend action or escalation
- Generate alerts or notifications
- Collapse history into snapshots that obscure sequence
- Color-code or visually emphasize evaluative meaning

Any transformation that answers "what matters" or "what should be done" is forbidden.

---

## Predicate Transparency Rule
For any query that reduces a set of events into a subset or aggregate:
> **The predicate used must be displayed before results are shown.**

The system must restate the predicate in literal, mechanical terms.
The query layer must never imply that the predicate is normative, correct, or preferred.

---

## Instance-First Rule
If a number is presented, the corresponding set of instances must be:
- Directly accessible
- Identifiable
- Navigable

There must be no orphan aggregates.

---

## Relationship to Interpretation
Queries may answer:
- "What happened?"
- "When did it happen?"
- "Which events meet this rule?"

Queries must never answer:
- "Why did this happen?"
- "Is this bad?"
- "What should be done?"

Interpretation boundaries are defined in `constitution/CORE_INTERPRETATION_BOUNDARY.md` and `constitution/CORE_LEDGER_BOUNDARY.md`.

---

## Litmus Test
For any query feature or presentation:
> **Could a reasonable user believe the system is telling them what something means?**

If yes, the feature violates this constitution.

---

## Final Constraint
The query layer exists to preserve epistemic integrity.
Convenience must never override consequence-bound interpretation.
