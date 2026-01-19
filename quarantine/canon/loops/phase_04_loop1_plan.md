---
doc_id: quarantine_phase_04_loop1_plan
doc_type: context
status: quarantined
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [quarantine]
---

Source: Cutter Layers/canon/loops/phase_04_loop1_plan.md

---
doc_id: phase_04_loop1_plan
doc_type: spec
status: active
version: 0.1
date: 2026-01-16
owner: Erik
authoring_agent: chatgpt
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: []
source: chatgpt
locks: [phases_1_2_3]
---

# Phase 4 — Loop 1 Execution Plan

## PR-Sized Tasks

1. Freeze identifier & encoding conventions  
   Lane: Execution  
   DoD: State uses entity_ref + scope_ref = promise:deadline and JSON {"deadline":"<ISO-8601>"} only; no Ops nouns. Cutter uses literal event_type and event_data.stage allowed values.

2. Define promise:deadline state schema  
   Lane: Execution  
   DoD: entity_ref format validated; scope_ref = promise:deadline; state_text JSON with deadline only.

3. Emit stage_started / stage_completed exhaust  
   Lane: Execution  
   DoD: machining, inspection, packing only; boundary-respecting.

4. Emit carrier_handoff event  
   Lane: Execution  
   DoD: single factual event; no closure logic.

5. Add Ops config for expected stage durations  
   Lane: Execution  
   DoD: read-only expectations; not written to ledgers.

6. Implement Query A (open promise:deadline declarations)  
   Lane: Execution  
   DoD: anti-join only; raw rows.

7. Implement Query B (dwell-time vs expectation)  
   Lane: Execution  
   DoD: arithmetic only; no thresholds.

8. Natural language → query router  
   Lane: Quarantine  
   DoD: explicit phrase table; unknown phrases rejected.

9. Minimal UX surface for Loop 1  
   Lane: Discussion  
   DoD: raw outputs only; no implied judgment.

10. Demo dataset + cadence ritual  
   Lane: Execution  
   DoD: deterministic data; weekly ritual exercises both queries.
