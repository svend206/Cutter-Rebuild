---
doc_id: core_local_first
doc_type: constitution
status: locked
version: 1.0
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: []
conflicts_with: []
tags: [local_first, storage, database]
---

# Local-First and Persistence Constraints (Constitutional)

## Purpose
Guarantee that Cutter remains locally sovereign and operable without network dependence.

---

## Core Constraints
1. **Offline-first by default**  
   Core functionality MUST operate without a network connection.

2. **No required external services**  
   No external API or hosted dependency may be required for core functionality.

3. **Local assets only**  
   All JS/CSS/3D libraries required for core functionality MUST be served locally.

4. **SQLite-only storage**  
   The authoritative operational database MUST be SQLite.

5. **WAL mode required**  
   All SQLite connections MUST enable `PRAGMA journal_mode=WAL;` for durability.

---

## Notes
Optional network features may exist only if:
- core functionality remains fully usable offline
- network features are explicitly enabled by the user
