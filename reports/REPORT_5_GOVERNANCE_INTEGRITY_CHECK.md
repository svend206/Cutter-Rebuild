---
doc_id: report_governance_integrity_check
doc_type: context
status: active
version: 1.1
date: 2026-01-19
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources:
  - DIRECTORY.md
  - boot/BOOT_CONTRACT.md
  - integrator/INTEGRATOR_HOME.md
  - architecture/NAVIGATION_INDEX.md
  - bootstrap/CONSTITUTION_INDEX.md
conflicts_with: []
tags: [report, governance, context]
---

# REPORT 5 — GOVERNANCE INTEGRITY CHECK

## Single Boot Contract
- Present and registered.
  Evidence: `boot/BOOT_CONTRACT.md`, `DIRECTORY.md`

## Single Status Surface
- `integrator/INTEGRATOR_HOME.md` only.
  Evidence: `integrator/INTEGRATOR_HOME.md`, `DIRECTORY.md`

## Single App Entrypoint
- Root `app.py` is the entrypoint shim to `ops_layer/app.py`.
  Evidence: `app.py`

## No Duplicate Constitutional Authority
- Constitution index lists authoritative constitutional files without duplicates.
  Evidence: `bootstrap/CONSTITUTION_INDEX.md`

## Navigation/Index Docs Are Pointers (Context Only)
- Navigation index explicitly states non-binding guidance.
  Evidence: `architecture/NAVIGATION_INDEX.md`

## Authority Registry and Context Boundaries
- `DIRECTORY.md` is the authority registry and load order for all authoritative docs.
  Evidence: `DIRECTORY.md`
- Context documents are non-authoritative and do not govern behavior.
  Evidence: `constitution/CORE_DOC_GOVERNANCE.md`, `DIRECTORY.md`

## Violations
- None found in repository artifacts reviewed for this report.
