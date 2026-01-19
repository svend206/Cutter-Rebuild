---
doc_id: quarantine_scripts_readme
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

Source: Cutter Layers/scripts/README.md

# Scripts Directory

Utility scripts and demonstrations for the Cutter Layers system.

---

## Boot Path (Required)
1. From repo root: `python scripts/reset_db.py` (first-time or missing ledgers).
2. Then: `python app.py`.
3. `app.py` will refuse to start if cutter/state tables or append-only triggers are missing.
4. PROD mode: `TEST_DB_PATH` unset → uses `cutter.db`.
5. TEST mode: `TEST_DB_PATH` set → must be a non-prod test path (contains "test").

---

## Reset Local Database

**File**: `reset_db.py`

**Purpose**: Safely reset local database for development (never deletes data - moves to backup).

**What it does**:
1. Moves existing `cutter.db` to `./data/backups/` with timestamp
2. Creates fresh database using canonical initialization
3. Verifies core tables exist (ops__, cutter__, state__)
4. Prints success summary

**Usage**:
```bash
# Reset default database (cutter.db)
python scripts/reset_db.py

# Reset custom database
python scripts/reset_db.py --db-path ./test.db
```

**Safety Features**:
- **Never deletes** - Always moves to timestamped backup
- **Backup location**: `./data/backups/cutter_backup_YYYYMMDD_HHMMSS.db`
- **Canonical initialization**: Uses `database.initialize_database()`
- **Verification**: Confirms all required tables created

**Use Cases**:
- Fresh start for development
- Clean testing environment
- After schema migrations
- Before registering State Ledger entities

**Output Example**:
```
======================================================================
DATABASE RESET SCRIPT
======================================================================

Target: cutter.db
Backup: data/backups/

[BACKUP] Moving existing database...
  From: cutter.db
  To:   data/backups/cutter_backup_20260112_120000.db

[CREATE] Initializing fresh database...
  Path: cutter.db
[SUCCESS] Database initialized

[VERIFY] Checking core tables...
  ✓ ops__quotes
  ✓ ops__parts
  ✓ ops__customers
  ✓ ops__contacts
  ✓ cutter__events
  ✓ state__entities
  ✓ state__recognition_owners
  ✓ state__declarations

[SUCCESS] All 8 required tables exist

======================================================================
DATABASE RESET COMPLETE
======================================================================

Backup: data/backups/cutter_backup_20260112_120000.db
  Size: 145.2 KB

Fresh DB: cutter.db
  Size: 96.0 KB

Ready for:
  - Fresh quote data entry
  - State Ledger entity registration
  - Clean testing environment

======================================================================
```

**Warning**: Local development only. Do not use in production.

---

## Weekly Ritual

**File**: `weekly_ritual.py`

**Purpose**: Print raw structural visibility from State Ledger and Cutter Ledger. No summaries, no advice, no "you should" statements - raw data only.

**What it prints**:
- **DS-2 (Unowned Recognition)**: Entities with no current recognition owner
- **DS-5 (Deferred Recognition)**: Entities past their expected cadence window
- **Optional**: Last N Cutter Ledger events

**Usage**:
```bash
# From repository root

# Basic ritual (DS-2 + DS-5)
python scripts/weekly_ritual.py

# Include last 20 Cutter events
python scripts/weekly_ritual.py --events 20

# Write to file instead of stdout
python scripts/weekly_ritual.py --output weekly_report.json

# Combine options
python scripts/weekly_ritual.py --events 50 --output weekly_ritual.json
```

**Output Format**:
```json
{
  "ritual": "weekly_structural_visibility",
  "timestamp": "2026-01-12T05:45:00",
  "constitutional_note": "Raw visibility only. No summaries, advice, or enforcement.",
  "ds2_unowned_recognition": {
    "description": "Entities with no current recognition owner",
    "count": 2,
    "entities": [
      {
        "entity_ref": "org:cutter-layers/entity:customer:abc",
        "entity_label": "ABC Manufacturing",
        "cadence_days": 30,
        "created_at": "2026-01-01T10:00:00"
      }
    ]
  },
  "ds5_deferred_recognition": {
    "description": "Entities past expected reaffirmation cadence",
    "count": 1,
    "entities": [
      {
        "entity_ref": "org:cutter-layers/entity:equipment:cnc-1",
        "entity_label": "Primary CNC Mill",
        "cadence_days": 1,
        "last_declaration_at": "2026-01-10T08:00:00",
        "days_since_last_declaration": 2
      }
    ]
  },
  "recent_cutter_events": {
    "description": "Last 20 operational events from Cutter Ledger",
    "count": 20,
    "total_events_in_ledger": 156,
    "events": [ ... ]
  }
}
```

**Exit Code**: Always 0 (unless database is missing). Visibility is not enforcement.

**Constitutional Compliance**:
- ✅ No summaries or interpretations
- ✅ No advice or "you should" statements
- ✅ Raw data visibility only
- ✅ Exit code 0 (queryable, not actionable)

**Recommended Cadence**: Weekly (hence the name), but run as often as needed.

**Integration**: Can be run manually, scheduled via cron, or integrated into team rituals/standups.

---

## Ledger Query CLI

**File**: `ledger_query_cli.py`

**Purpose**: Read-only CLI query interface for Cutter Ledger and State Ledger.

**Constitutional enforcement**: Raw output only. No summaries, recommendations, alerts, health checks, or scoring. Makes data queryable, not actionable.

### State Ledger Commands

```bash
# List all registered entities
python scripts/ledger_query_cli.py state list-entities

# Get latest declarations (most recent first)
python scripts/ledger_query_cli.py state latest-declarations
python scripts/ledger_query_cli.py state latest-declarations --entity_ref org:acme/entity:customer:123
python scripts/ledger_query_cli.py state latest-declarations --scope_ref org:acme/scope:weekly --limit 5

# Query declarations with full filtering
python scripts/ledger_query_cli.py state declarations --entity_ref org:acme/entity:customer:123
python scripts/ledger_query_cli.py state declarations --scope_ref org:acme/scope:monthly
python scripts/ledger_query_cli.py state declarations --actor_ref org:acme/actor:alice --limit 10

# Query derived states (structural visibility)
python scripts/ledger_query_cli.py state ds1  # Persistent Continuity (2+ reaffirmations)
python scripts/ledger_query_cli.py state ds2  # Unowned Recognition (no current owner)
python scripts/ledger_query_cli.py state ds5  # Deferred Recognition (past cadence window)
```

### Cutter Ledger Commands

```bash
# Query events
python scripts/ledger_query_cli.py cutter events
python scripts/ledger_query_cli.py cutter events --subject_ref quote:123
python scripts/ledger_query_cli.py cutter events --event_type quote_overridden --limit 10

# Query override events specifically
python scripts/ledger_query_cli.py cutter overrides
```

### Output Format

- JSON (pretty-printed by default)
- Use `--no-pretty` for compact JSON

### Environment

- Respects `TEST_DB_PATH` for hermetic testing
- Uses production `cutter.db` by default

### Examples

```bash
# Get all unowned entities
python scripts/ledger_query_cli.py state ds2

# Get recent declarations for a specific entity
python scripts/ledger_query_cli.py state latest-declarations \
  --entity_ref org:shop-a/entity:customer:cust-001 \
  --limit 5

# Get all override events for a quote
python scripts/ledger_query_cli.py cutter events \
  --subject_ref quote:456 \
  --event_type quote_overridden
```

---

## End-to-End Demo

**File**: `demo_end_to_end.py`

**Purpose**: Comprehensive demonstration of the complete flow through all three layers: Ops → Cutter Ledger → State Ledger → CLI Queries.

**What it demonstrates**:
- **Phase 1**: Ops Layer emits operational exhaust to Cutter Ledger
  - Price override event
  - Quote finalized event
  - Query events for a specific subject
- **Phase 2**: State Ledger captures explicit recognition
  - Entity registration
  - Owner assignment
  - 1 RECLASSIFICATION declaration
  - 2 REAFFIRMATION declarations (proves DS-1 continuity)
  - Links to Cutter Ledger event as evidence
- **Phase 3**: CLI-style queries demonstrate data visibility
  - List entities
  - Latest declarations
  - DS-1: Persistent Continuity (2+ reaffirmations)
  - DS-2: Unowned Recognition (no current owner)
  - DS-5: Deferred Recognition (past cadence window)
  - All declarations for an entity

**Usage**:
```bash
# From repository root
python scripts/demo_end_to_end.py
```

**Output**: 
- Raw JSON for all queries
- Console output showing each phase
- Constitutional compliance verification

**Environment**:
- Uses `TEST_DB_PATH` if set, otherwise creates temp database
- Preserves database after completion for manual inspection

**Constitutional compliance**:
- Append-only ledgers (no UPDATE/DELETE)
- Raw output only (no interpretation)
- No summaries or advice
- Explicit recognition (no inference)

---

## State Ledger Demo

**File**: `state_ledger_demo.py`

**Purpose**: Focused demonstration of State Ledger constitutional behavior.

**What it demonstrates**:
- Entity registration and recognition ownership
- Declaration emissions (RECLASSIFICATION and REAFFIRMATION)
- Derived state detection (DS-1, DS-2, DS-5)
- Constitutional refusals:
  - Wrong owner (DS-2: No Proxy Recognition)
  - Missing owner (DS-2: Unowned Recognition)
  - Append-only enforcement (C4: Irreversible Memory)

**What it does NOT do**:
- No inference or interpretation
- No summaries or advice
- No UI or alerts
- No dashboard or scoring

**Usage**:
```bash
# From repository root
python scripts/state_ledger_demo.py
```

**Output**: Raw results and refusal messages only. No interpretation.

**Requirements**:
- `cutter.db` must exist (run migrations first if needed)
- State Ledger tables must be present (Phase 5 migrations)

---

## Server Management

**Files**: `start_server.ps1` / `kill_server.ps1`

**Purpose**: PowerShell utilities for managing the Flask development server.

**Usage**:
```powershell
# Start server in background
.\scripts\start_server.ps1

# Stop server
.\scripts\kill_server.ps1
```

---

## Notes

- All scripts are deterministic and non-interactive
- All scripts respect the `TEST_DB_PATH` environment variable for hermetic testing
- No script modifies production data patterns without explicit intent
