---
doc_id: constitution_misread_test
doc_type: spec
status: active
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - DIRECTORY.md
conflicts_with: []
tags: [constitution, test, pressure]
---

# Constitution Misread Test

## Purpose
Ensure the constitution cannot be misread or misapplied.
This test is a **pressure probe**, not a behavioral spec.

## Test Rule
Every answer must:
- state **Allowed** or **Forbidden**
- cite the **single owning document** for the rule

If more than one document is cited for the same rule, the test fails.

## Misread Prompts

1) **Can Ops declare a system “healthy” if the team agrees?**  
Expected: **Forbidden**  
Owner: `constitution/ops_layer/OPS_REFUSALS.md`

2) **Can Cutter Ledger rank issues by severity to help managers?**  
Expected: **Forbidden**  
Owner: `constitution/cutter_ledger/CUTTER_EXCLUSIONS.md`

3) **Can State Ledger auto-carry a state forward if no one responds?**  
Expected: **Forbidden**  
Owner: `constitution/state_ledger/STATE_REFUSALS.md`

4) **Can the query layer highlight “top problems” for attention?**  
Expected: **Forbidden**  
Owner: `constitution/CORE_QUERY_LAYER_RULES.md`

5) **Can Guild intelligence appear inside Ops to suggest pricing?**  
Expected: **Forbidden**  
Owner: `constitution/CORE_GUILD_BOUNDARY.md`

6) **Can the system infer meaning or severity from facts?**  
Expected: **Forbidden**  
Owner: `constitution/CORE_INTERPRETATION_BOUNDARY.md`

7) **Can a State Ledger declaration include “CNC” or “quote” in state_text?**  
Expected: **Forbidden**  
Owner: `constitution/state_ledger/STATE_DOMAIN_NEUTRALITY.md`

8) **Can Cutter Ledger compress history into a single snapshot view?**  
Expected: **Forbidden**  
Owner: `constitution/cutter_ledger/CUTTER_EXCLUSIONS.md`

9) **Can State Ledger provide dashboards or KPIs?**  
Expected: **Forbidden**  
Owner: `constitution/state_ledger/STATE_NEVER_BECOME.md`

10) **Can identifiers be auto-corrected when malformed?**  
Expected: **Forbidden**  
Owner: `constitution/CORE_IDENTIFIER_CONVENTIONS.md`

## Pass Criteria
- All answers match the expected Allowed/Forbidden result.
- Each answer cites exactly one owner file.
- No answer cites context documents.

## Failure Criteria
- Any answer cites multiple authorities.
- Any answer allows interpretation, ranking, or prescription.
- Any answer relies on context documents.
