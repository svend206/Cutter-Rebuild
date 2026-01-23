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

## No Known Deferral Rule
When a known issue, weakness, or inconsistency is discovered during work, and it can be resolved safely within the current scope and authority, it must be resolved immediately.

Deferral is permitted only when at least one of the following is true:
- Fixing it now would violate a locked constraint, phase rule, or explicit scope boundary.
- Fixing it now would weaken an invariant or require authority not granted.
- The issue cannot be safely resolved with current information and acting now would introduce risk.
- Fixing it now would require a broad refactor that changes behavior beyond the current task.

If an issue is deferred, the deferral must be explicit and recorded:
- what is being deferred
- why it meets one of the allowed exceptions
- where it lives (file, path, endpoint, or component)

Silence is not an acceptable deferral mechanism.
“OK for now” is not a justification.

## Promotion Discipline
Legacy artifacts from the old repo are read-only. Promotion into this repo must be explicit.

## Preconditions
Action is forbidden unless `DIRECTORY.md` and `integrator/INTEGRATOR_HOME.md` have been read and Integrator Home has been updated as needed. Any task not listed in Integrator Home is inactive.

## Refusal
If this contract is not acknowledged or is missing, agents must refuse to act.

## Scope
Applies to humans, Cursor, and external AI equally.
