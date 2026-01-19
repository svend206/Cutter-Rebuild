---
doc_id: mode_seperation
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
tags: [ops, mode, separation]
---

# Ops Layer: Separation of Execution and Planning

## Core Distinction

- Execution and planning are distinct cognitive phases.
- Execution and planning must not be mixed in the Ops layer.
- Execution and planning require different information surfaces.
- Execution and planning require different permissions.
- Execution and planning require different constraints.
- Execution and planning must be intentionally separated by the system.

---

## Execution Mode Characteristics

- Execution occurs while work is in progress.
- Execution occurs under time pressure.
- Execution occurs under uncertainty.
- Execution involves firefighting.
- Execution involves judgment calls.
- Execution involves overrides and exceptions.
- Execution involves acting, not reflecting.

---

## Execution Mode Constraints

- No pattern matching during execution.
- No aggregation during execution.
- No dashboards during execution.
- No metrics during execution.
- No recommendations during execution.
- No interpretation during execution.
- No explanation capture ("why") during execution.
- No optimization during execution.
- No comparison to norms during execution.
- No guidance presented during execution.

---

## Execution Mode Responsibilities

- Show only what is immediately actionable.
- Allow rapid state changes.
- Allow overrides without explanation.
- Record all state changes.
- Record all interventions.
- Preserve full history of actions.
- Preserve timing of actions.
- Preserve attribution of actions.

---

## Planning Mode Characteristics

- Planning occurs outside live execution.
- Planning occurs when time pressure is reduced.
- Planning allows reflection.
- Planning allows pattern recognition.
- Planning allows aggregation.
- Planning allows comparison.
- Planning allows discomfort.
- Planning allows acknowledgement of burden.

---

## Planning Mode Permissions

- Interpretation is allowed in planning.
- Pattern matching is allowed in planning.
- Aggregation is allowed in planning.
- Historical analysis is allowed in planning.
- Recognition of repeated intervention is allowed.
- Identification of fragility is allowed.
- Decisions about future changes are allowed.

---

## Mode Separation

- The system must know which mode the user is in.
- Mode switching must be explicit.
- Mode switching must not be accidental.
- Mode switching may involve friction.
- Mode switching may involve ceremony.
- The system must not silently cross modes.
- Information permitted in one mode may be forbidden in the other.

---

## Rationale Constraints (Non-Interpretive)

- Information presented under pressure affects behavior.
- Information under pressure functions as instruction.
- Mixing interpretation with execution degrades execution quality.
- Execution quality is harmed by mid-action analysis.
- Execution quality benefits from reduced cognitive load.

---

## Relationship to Ops Layer

- Ops layer is responsible for execution support.
- Ops layer is responsible for recording events.
- Ops layer is not responsible for interpretation.
- Ops layer is not responsible for learning.
- Ops layer is not responsible for optimization.
- Ops layer emits exhaust.
- Ops layer preserves raw signals.

---

## Explicit Non-Goals

- Ops layer does not teach.
- Ops layer does not coach.
- Ops layer does not guide decisions.
- Ops layer does not recommend actions.
- Ops layer does not evaluate performance.
- Ops layer does not collapse history.

---

## Interaction with Other Layers

- Planning outputs may inform future execution preparation.
- Interpretation may occur outside Ops.
- Learning may occur outside Ops.
- Pattern extraction may occur outside Ops.
- Ops remains phase-pure.

