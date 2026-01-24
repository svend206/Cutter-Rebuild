---
doc_id: phase_vi_work_charter
doc_type: spec
status: draft
version: 0.1
date: 2026-01-24
owner: Erik
authoring_agent: architect
supersedes: []
superseded_by: []
authoritative_sources: [boot/PROJECT_PHASE_CONSTITUTION.md]
conflicts_with: []
tags: [phase, operability, charter, spec]
---

# Phase VI — Work Charter (Operability)

Phase: VI — Operability

Status: Draft

---

## Intent

Phase VI exists to ensure the system can operate continuously
**without epistemic degradation**.

This phase governs what happens when parts of the system:
- fail,
- degrade,
- become unavailable,
- behave unexpectedly,
- or produce outputs whose provenance is incomplete.

Operability here does **not** mean:
- “healthy”
- “safe”
- “correct”
- “recommended”
- “trustworthy by default”

Operability means only:
- failures are visible,
- behavior under degradation is deterministic,
- refusals are explicit,
- and the system does not lie to preserve continuity.

---

## Allowed Work (This Phase Only)

During Phase VI, work may include:

- Cataloging runtime failure modes across the whole system, including:
  - storage unavailable / slow / partial
  - write path failure
  - read path failure
  - ordering / time-source ambiguity
  - partial persistence (some records written, others not)
  - dependency failure (queue, cache, network, auth, clock)
  - corrupted inputs or invalid records
  - schema/format mismatch between components
  - “unknown state” conditions (cannot know whether X occurred)

- Defining how failures are **surfaced visibly** to operators and users, including:
  - what is shown
  - where it is shown
  - what words are permitted
  - what is strictly forbidden language

- Defining deterministic refusal behavior under degraded operation:
  - what the system will refuse
  - what the system may still allow
  - what the system must record about the refusal
  - how refusal is made stable (“same failure → same refusal”)

- Defining operator-visible operational signals **without evaluation**, including:
  - “this component is unavailable”
  - “this action could not be completed”
  - “this record may not be durable”
  - “ordering cannot be guaranteed”
  - “data may be incomplete”
  - “the system cannot know whether X occurred”

All output in this phase must remain:
- descriptive, not evaluative
- explicit, not inferred
- refusal-forward, not reassurance-forward

---

## Forbidden Work

During Phase VI, the project must not:

- Define correctness of domain outputs
- Introduce “health” scoring, status grades, or comfort labels
  (green/yellow/red, “OK”, “good”, “degraded but safe”, etc.)
- Optimize for uptime at the cost of truth, provenance, or visibility
- Suppress or hide failures to preserve continuity of operation
- Imply the system is “safe” because it is running
- Add recommendations, urgency, or “what you should do next”
- Add automatic fallbacks that silently change semantics
- Convert uncertainty into implied completeness

If a mechanism reduces operator anxiety by hiding reality, it is forbidden.

---

## Operability Invariants (Phase VI Specific)

These invariants apply to every failure mode response defined in this phase:

### VI-1 — Fail Loudly
Failure must be visible at the point of use.
No silent failure, no “best effort” without disclosure.

### VI-2 — Refuse Deterministically
If the system cannot perform an action within defined guarantees,
it must refuse clearly and repeatably.

### VI-3 — Preserve Uncertainty
If the system cannot know whether something happened,
it must say so explicitly and durably.
It must not guess.

### VI-4 — No Semantic Fallbacks Without Disclosure
Any fallback behavior must be explicitly visible as a different mode.
Silent fallback is forbidden.

### VI-5 — No Epistemic Debt
The system must not “paper over” missing durability or ordering
to keep the UI smooth.
If guarantees are absent, that absence must be shown.

---

## Required Artifacts (to Exit Phase VI)

Before Phase VI can end, the following must exist:

1) **Failure-Mode Catalog (Runtime)**
- Enumerated failure modes
- Triggers / detection conditions (descriptive only)
- What the system can and cannot know in each mode

2) **Degradation Refusal Semantics**
For each failure mode:
- what actions are refused
- what actions may proceed (if any)
- what is recorded about refusal
- how “unknown completion” is represented

3) **Operator-Visible Surface Rules**
- What failure/degradation text is permitted
- What language is forbidden (reassurance, scoring, “safe”, “healthy”, etc.)
- Where the failure is shown so it cannot be missed

4) **Explicit Statement of What “Operational” Does Not Mean**
A durable statement that explicitly denies:
- safety
- correctness
- completeness
- recommendation
- fitness for purpose by default

5) **Adversarial Operability Audit (Human-Run)**
A recorded audit attempting to demonstrate:
- silent failure exists
- partial failure is hidden
- semantic fallback is silent
- uncertainty is converted into implied completion
- refusals differ across identical conditions

Audit outcome is binary (PASS/FAIL).

---

## Known Unknowns (Intentionally Preserved)

The following are explicitly not to be resolved in Phase VI:

- Performance targets (“fast enough”)
- Uptime targets (“five nines”)
- Cost optimization
- User training, playbooks, or best practices
- What an operator “should” do during failure
- Any claim that failure handling produces better outcomes

This phase defines truth-preserving behavior, not operational excellence.

---

## Exit Condition (Human Judgment)

Phase VI ends only when a reviewer can say:

> “When this breaks, it breaks loudly, honestly, and without lying.”

And when the adversarial operability audit cannot demonstrate:
- hidden failure,
- semantic fallback without disclosure,
- or implied completeness under uncertainty.
