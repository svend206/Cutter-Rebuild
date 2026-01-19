---
doc_id: boot_contract
doc_type: spec
status: active
version: 1.5
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [boot, governance]
---

# Boot Contract

This contract gates all action in this repository.

## Authority
- The Constitution is the highest authority.
- This Boot Contract is operational and may not override the Constitution.
- Integrator Home is the only source of current operational truth.
- Document authority and validity are governed by `constitution/CORE_DOC_GOVERNANCE.md` and the registry in `DIRECTORY.md`.
- Context documents are non-authoritative and must not be treated as rules.

## Non-Invention
Agents may not invent requirements, rules, or scope that are not explicitly written in authoritative documents.

## Promotion Discipline
Legacy artifacts from the old repo are read-only. Promotion into this repo must be explicit.

## Preconditions
Action is forbidden unless `DIRECTORY.md` and `integrator/INTEGRATOR_HOME.md` have been read and Integrator Home has been updated as needed. Any task not listed in Integrator Home is inactive.

## Refusal
If this contract is not acknowledged or is missing, agents must refuse to act.

## Scope
Applies to humans, Cursor, and external AI equally.
