---
doc_id: classification_log
doc_type: context
status: quarantined
version: 1.1
date: 2026-01-18
owner: Erik
authoring_agent: cursor
supersedes: []
superseded_by: []
authoritative_sources: [architecture/PROMOTION_CHECKLIST.md]
conflicts_with: []
tags: [quarantine, classification]
---

# Old Repo Classification Log

Log every file from `C:\Users\esacu\Desktop\Cutter Layers` (excluding `scaffold/**`).
Rules are applied top-to-bottom; first match wins. `source_path` may be a path or a glob pattern.

## Columns

- source_path
- file_type (doc | code | data | asset | config | other)
- disposition (promote | rewrite_then_promote | archive | reject | quarantine)
- reason (short, explicit)
- batch_id
- status (pending | done)

## Log

| source_path | file_type | disposition | reason | batch_id | status |
| --- | --- | --- | --- | --- | --- |
| `scaffold/**` | other | reject | Explicitly excluded by rule | batch-2026-01-18-full | done |
| `.git/**` | other | reject | Git metadata excluded | batch-2026-01-18-full | done |
| `**/__pycache__/**` | data | reject | Python cache artifacts | batch-2026-01-18-full | done |
| `**/*.pyc` | data | reject | Python bytecode artifacts | batch-2026-01-18-full | done |
| `backups/**` | data | archive | Database backup artifacts | batch-2026-01-18-full | done |
| `data/**` | data | archive | Runtime data and backups | batch-2026-01-18-full | done |
| `archive/**` | other | archive | Legacy archive subtree | batch-2026-01-18-full | done |
| `docs_for_page_purpose_spec_review/**` | doc | quarantine | Legacy review bundle | batch-2026-01-18-full | done |
| `Docs/**` | doc | quarantine | Legacy docs bundle | batch-2026-01-18-full | done |
| `canon/**` | doc | quarantine | Legacy canon docs | batch-2026-01-18-full | done |
| `reports/**` | doc | quarantine | Legacy reports | batch-2026-01-18-full | done |
| `scripts/**` | code | quarantine | Legacy code; route to product intake | batch-2026-01-18-full | done |
| `tests/**` | code | quarantine | Legacy tests; route to product intake | batch-2026-01-18-full | done |
| `migrations/**` | code | quarantine | Legacy migrations; route to product intake | batch-2026-01-18-full | done |
| `ops_layer/**` | code | quarantine | Legacy ops code; route to product intake | batch-2026-01-18-full | done |
| `cutter_ledger/**` | code | quarantine | Legacy ledger code; route to product intake | batch-2026-01-18-full | done |
| `state_ledger/**` | code | quarantine | Legacy ledger code; route to product intake | batch-2026-01-18-full | done |
| `state_vault/**` | code | quarantine | Legacy vault code; route to product intake | batch-2026-01-18-full | done |
| `**/*.md` | doc | quarantine | Legacy docs pending review | batch-2026-01-18-full | done |
| `**/*.txt` | doc | quarantine | Legacy text docs pending review | batch-2026-01-18-full | done |
| `**/*.pdf` | asset | archive | Generated PDFs and artifacts | batch-2026-01-18-full | done |
| `**/*.STEP` | asset | quarantine | CAD assets pending review | batch-2026-01-18-full | done |
| `**/*.STL` | asset | quarantine | CAD assets pending review | batch-2026-01-18-full | done |
| `**/*.db` | data | archive | Database artifacts | batch-2026-01-18-full | done |
| `**/*.zip` | asset | quarantine | Bundled assets pending review | batch-2026-01-18-full | done |
| `**/*.log` | data | quarantine | Log artifacts pending review | batch-2026-01-18-full | done |
| `**/*.ps1` | code | quarantine | Legacy scripts; route to product intake | batch-2026-01-18-full | done |
| `**/*.js` | code | quarantine | Legacy frontend code; route to product intake | batch-2026-01-18-full | done |
| `**/*.css` | code | quarantine | Legacy frontend code; route to product intake | batch-2026-01-18-full | done |
| `**/*.html` | code | quarantine | Legacy frontend code; route to product intake | batch-2026-01-18-full | done |
| `**/*.yml` | config | quarantine | Legacy config pending review | batch-2026-01-18-full | done |
| `**/*.yaml` | config | quarantine | Legacy config pending review | batch-2026-01-18-full | done |
| `**/*.json` | config | quarantine | Legacy config pending review | batch-2026-01-18-full | done |
| `**/*.ini` | config | quarantine | Legacy config pending review | batch-2026-01-18-full | done |
| `**/*.cfg` | config | quarantine | Legacy config pending review | batch-2026-01-18-full | done |
| `**/*.toml` | config | quarantine | Legacy config pending review | batch-2026-01-18-full | done |
| `**/*` | other | quarantine | Legacy artifact pending review | batch-2026-01-18-full | done |
