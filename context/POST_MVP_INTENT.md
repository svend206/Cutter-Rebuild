---
doc_id: post_mvp_intent_20260122
doc_type: context
status: active
version: 1.0
date: 2026-01-22
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [context/MVP_CAPABILITIES_LOCKED.md]
conflicts_with: []
tags: [mvp, intent, post-mvp, context]
---

# Post-MVP Intent

MVP behavior is frozen.

## Execution / Discussion / Quarantine
Execution: work that preserves locked MVP behavior and verification.
Discussion: design and analysis work that does not change behavior.
Quarantine: speculative artifacts that must not affect the repo until promoted.

## Active Post-MVP Thread
Placeholder: none selected.

## Rules
- Post-MVP work must be declared as a capability (not UX/workflow).
- New capabilities must include proof + failure-mode proof.
- MVP invariants must not be weakened.

## Local Hooks (Optional)
To enable local pre-push hooks:
`git config core.hooksPath .githooks`
