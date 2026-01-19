---
doc_id: promotion_checklist
doc_type: context
status: active
version: 1.1
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [constitution/CORE_DOC_GOVERNANCE.md]
conflicts_with: []
tags: [promotion, checklist, context]
---

# Promotion Checklist (Old Repo → New Repo)

Use this checklist before promoting any artifact from `Cutter Layers`.

## 0) Inventory scope
- [ ] Enumerate all files in the old repo
- [ ] Exclude `scaffold/**` entirely (reject by rule)
- [ ] Process remaining files in batches with a recorded log entry per file

## 0a) Classification log (required)
- [ ] Record every file in `quarantine/CLASSIFICATION_LOG.md`
- [ ] Include: source_path (path or glob), file_type, disposition, reason, batch_id, status
- [ ] If using glob rules, apply top-to-bottom and mark as done
- [ ] Non-doc artifacts (code, data, assets) still get logged and routed to product intake

## 1) Classify the document
- [ ] Constitution / Decision Log / Spec / Context / Archive / Quarantine
- [ ] If not a doc (code, data, asset), stop and route to product intake

## 2) Authority & scope gate
- [ ] If it defines rules/invariants → Constitution candidate
- [ ] If it records a binding decision → Decision log candidate
- [ ] If it specifies behavior/requirements → Spec candidate
- [ ] If it explains rationale/vision → Context candidate
- [ ] If it is superseded or procedural → Archive

## 3) Redundancy / conflict check
- [ ] Map each rule or constraint to a single owner in the new repo
- [ ] If already covered, do **not** promote (reject or archive)
- [ ] If overlap exists, resolve by supersession, not duplication

## 3a) Project Compatibility Gate
- [ ] Verify the document is compatible with the current project purpose and constitutional boundaries
- [ ] If compatibility is uncertain, stop and surface the issue(s) to the owner one by one

## 4) Format & placement
- [ ] Add YAML header if missing (before promotion)
- [ ] Place in the correct folder by doc_type
- [ ] Prefer updating an existing document over creating a new one

## 5) Atomic update rule
- [ ] Update `DIRECTORY.md` in the same change
- [ ] If constitutional change: add a decision log entry in the same change

## 6) Promotion decision
- [ ] Promote as-is
- [ ] Rewrite then promote
- [ ] Archive
- [ ] Reject
- [ ] Quarantine (context-only, non-authoritative)
