#!/usr/bin/env python3
"""
Database Reset Script - Local Development Only

Safely resets the local database by:
1. Moving existing DB to ./data/backups/ with timestamp (never deletes)
2. Creating fresh DB using canonical initialization
3. Verifying core tables exist

Constitutional compliance:
- Never deletes data (moves to backup)
- Deterministic initialization
- Local dev only (no production use)

Usage:
    python scripts/reset_db.py
    python scripts/reset_db.py --db-path ./custom.db
"""

# CUTTER: LEDGER_SQL_ALLOWED (BOOTSTRAP)

import sys
import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import database


def backup_existing_db(db_path: Path, backup_dir: Path) -> Path:
    """
    Move existing database to backup directory with timestamp.
    
    Args:
        db_path: Path to existing database
        backup_dir: Directory for backups
    
    Returns:
        Path to backed up database
    """
    if not db_path.exists():
        print(f"[INFO] No existing database at {db_path}")
        return None
    
    # Create backup directory if needed
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"cutter_backup_{timestamp}.db"
    backup_path = backup_dir / backup_name
    
    # Move (never delete)
    print(f"[BACKUP] Moving existing database...")
    print(f"  From: {db_path}")
    print(f"  To:   {backup_path}")
    
    shutil.move(str(db_path), str(backup_path))
    
    # Also backup WAL files if they exist
    wal_path = Path(str(db_path) + "-wal")
    shm_path = Path(str(db_path) + "-shm")
    
    if wal_path.exists():
        shutil.move(str(wal_path), str(backup_dir / f"cutter_backup_{timestamp}.db-wal"))
    if shm_path.exists():
        shutil.move(str(shm_path), str(backup_dir / f"cutter_backup_{timestamp}.db-shm"))
    
    return backup_path


def create_fresh_db(db_path: Path):
    """
    Create fresh database using canonical initialization.
    
    Args:
        db_path: Path where database should be created
    """
    print(f"\n[CREATE] Initializing fresh database...")
    print(f"  Path: {db_path}")
    
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing test DB to guarantee clean slate
    path_str = str(db_path).lower()
    if db_path.exists() and ("test" in path_str or "tests" in db_path.parts):
        db_path.unlink()
        wal_path = Path(str(db_path) + "-wal")
        shm_path = Path(str(db_path) + "-shm")
        if wal_path.exists():
            wal_path.unlink()
        if shm_path.exists():
            shm_path.unlink()
    
    # Create all tables directly - more reliable than module reloading
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Set WAL mode (constitutional requirement)
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Create Ops Layer tables directly
        # (Simplified from database.initialize_database())
        
        # ops__materials
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__materials (
                name TEXT PRIMARY KEY,
                cost_per_cubic_inch REAL NOT NULL,
                machinability_score REAL NOT NULL
            )
        """)
        
        # ops__shop_config
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__shop_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ops__quote_history (legacy)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__quote_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                fingerprint TEXT,
                anchor_price REAL,
                final_price REAL,
                setup_time INTEGER,
                user_feedback_tags TEXT,
                tag_weights TEXT,
                status TEXT DEFAULT 'Draft',
                actual_runtime REAL,
                is_guild_submission INTEGER DEFAULT 0,
                submission_date TEXT,
                exported_at TEXT,
                is_compliant INTEGER DEFAULT 1,
                is_deleted INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                loss_reason TEXT,
                win_notes TEXT,
                closed_at TEXT,
                material TEXT,
                genesis_hash TEXT,
                process_routing TEXT,
                source_type TEXT,
                reference_image TEXT,
                quote_id TEXT,
                handling_time REAL
            )
        """)
        
        # ops__customers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                domain TEXT NOT NULL,
                corporate_tags_json TEXT DEFAULT '[]',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ops__contacts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                current_customer_id INTEGER,
                behavior_tags_json TEXT DEFAULT '[]',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(current_customer_id) REFERENCES ops__customers(id)
            )
        """)
        
        # ops__parts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                genesis_hash TEXT UNIQUE NOT NULL,
                filename TEXT,
                fingerprint_json TEXT,
                volume REAL,
                surface_area REAL,
                dimensions_json TEXT,
                process_routing_json TEXT DEFAULT '[]',
                features_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ops__quotes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id TEXT UNIQUE NOT NULL,
                part_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                contact_id INTEGER,
                user_id INTEGER,
                material TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                target_date TEXT,
                payment_terms_days INTEGER DEFAULT 30,
                system_price_anchor REAL NOT NULL,
                final_quoted_price REAL NOT NULL,
                variance_json TEXT,
                pricing_tags_json TEXT,
                physics_snapshot_json TEXT,
                status TEXT DEFAULT 'Draft',
                notes TEXT,
                lead_time_date TEXT,
                lead_time_days INTEGER,
                target_price_per_unit REAL,
                price_breaks_json TEXT,
                outside_processing_json TEXT,
                quality_requirements_json TEXT,
                part_marking_json TEXT,
                win_notes TEXT,
                loss_reason TEXT,
                closed_at TEXT,
                win_attribution_json TEXT,
                loss_attribution_json TEXT,
                is_deleted INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(part_id) REFERENCES ops__parts(id) ON DELETE CASCADE,
                FOREIGN KEY(customer_id) REFERENCES ops__customers(id) ON DELETE RESTRICT,
                FOREIGN KEY(contact_id) REFERENCES ops__contacts(id) ON DELETE SET NULL
            )
        """)
        
        print(f"[OK] Ops Layer tables created")
        
        # ops__quote_outcome_events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__quote_outcome_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                outcome_type TEXT NOT NULL,
                actor_user_id INTEGER,
                saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                original_price REAL,
                final_price REAL,
                price_changed BOOLEAN DEFAULT FALSE,
                original_leadtime_days INTEGER,
                final_leadtime_days INTEGER,
                leadtime_changed BOOLEAN DEFAULT FALSE,
                original_terms_days INTEGER,
                final_terms_days INTEGER,
                terms_changed BOOLEAN DEFAULT FALSE,
                other_notes TEXT,
                wizard_completed BOOLEAN DEFAULT FALSE,
                wizard_step_reached INTEGER DEFAULT 0,
                FOREIGN KEY(quote_id) REFERENCES ops__quotes(id) ON DELETE CASCADE
            )
        """)
        
        # ops__custom_tags
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__custom_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                impact_type TEXT,
                impact_value REAL,
                persistence_type TEXT DEFAULT 'transient',
                category TEXT DEFAULT 'General'
            )
        """)

        # ops__reconciliations (MVP-12)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__reconciliations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope_ref TEXT NOT NULL,
                scope_kind TEXT NOT NULL CHECK (scope_kind IN ('query', 'report')),
                predicate_ref TEXT NOT NULL,
                predicate_text TEXT,
                actor_ref TEXT NOT NULL,
                reconciled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ops__saved_reports (Post-MVP planning-only)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops__saved_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_name TEXT NOT NULL UNIQUE,
                query_type TEXT NOT NULL,
                params_json TEXT NOT NULL,
                created_by_actor_ref TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_run_at TEXT
            )
        """)
        
        # Create Cutter Ledger tables (reuse connection)
        if conn is None or not hasattr(conn, 'cursor'):
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
        
        # Create cutter__events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cutter__events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                subject_ref TEXT NOT NULL,
                event_data TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                ingested_by_service TEXT,
                ingested_by_version TEXT
            )
        """)
        
        # Create append-only triggers for cutter__events
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS block_cutter_events_update
            BEFORE UPDATE ON cutter__events
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: cutter__events is append-only (no UPDATE)');
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS block_cutter_events_delete
            BEFORE DELETE ON cutter__events
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: cutter__events is append-only (no DELETE)');
            END
        """)
        
        print(f"[OK] Cutter Ledger tables created")
        
        # Create State Ledger tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state__entities (
                entity_ref TEXT PRIMARY KEY,
                entity_label TEXT NOT NULL,
                cadence_days INTEGER NOT NULL DEFAULT 7,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state__recognition_owners (
                entity_ref TEXT NOT NULL,
                owner_actor_ref TEXT NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
                unassigned_at TEXT,
                assigned_by_actor_ref TEXT NOT NULL,
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            )
        """)
        
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_one_current_owner
            ON state__recognition_owners(entity_ref)
            WHERE unassigned_at IS NULL
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state__declarations (
                declaration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_ref TEXT NOT NULL,
                scope_ref TEXT NOT NULL,
                state_text TEXT NOT NULL,
                declaration_kind TEXT NOT NULL CHECK (declaration_kind IN ('REAFFIRMATION','RECLASSIFICATION')),
                declared_by_actor_ref TEXT NOT NULL,
                declared_at TEXT NOT NULL DEFAULT (datetime('now')),
                supersedes_declaration_id INTEGER,
                cutter_evidence_ref TEXT,
                evidence_refs_json TEXT DEFAULT '[]',
                classification TEXT,
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            )
        """)
        
        # Create append-only triggers for state__declarations
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS block_state_declarations_update
            BEFORE UPDATE ON state__declarations
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: state__declarations is append-only (no UPDATE)');
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS block_state_declarations_delete
            BEFORE DELETE ON state__declarations
            BEGIN
                SELECT RAISE(ABORT, 'Constitutional violation: state__declarations is append-only (no DELETE)');
            END
        """)
        
        print(f"[OK] State Ledger tables created")
        
        # Create State Ledger derived-state views
        # DS-2: Unowned Recognition
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS view_ds2_unowned_recognition AS
            SELECT 
                e.entity_ref,
                e.entity_label,
                e.cadence_days,
                e.created_at as entity_created_at
            FROM state__entities e
            WHERE NOT EXISTS (
                SELECT 1 FROM state__recognition_owners o
                WHERE o.entity_ref = e.entity_ref
                AND o.unassigned_at IS NULL
            )
        """)
        
        # DS-5: Deferred Recognition
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS view_ds5_deferred_recognition AS
            SELECT 
                e.entity_ref,
                e.entity_label,
                e.cadence_days,
                MAX(d.declared_at) as last_declaration_at,
                CAST((JULIANDAY('now') - JULIANDAY(MAX(d.declared_at))) AS INTEGER) as days_since_last_declaration
            FROM state__entities e
            LEFT JOIN state__declarations d ON e.entity_ref = d.entity_ref
            GROUP BY e.entity_ref, e.entity_label, e.cadence_days
            HAVING 
                last_declaration_at IS NULL
                OR CAST((JULIANDAY('now') - JULIANDAY(last_declaration_at)) AS INTEGER) > e.cadence_days
        """)
        
        # DS-1: Persistent Continuity
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS view_ds1_persistent_continuity AS
            WITH last_reclassification AS (
                SELECT 
                    entity_ref,
                    scope_ref,
                    MAX(declaration_id) as last_recl_id
                FROM state__declarations
                WHERE declaration_kind = 'RECLASSIFICATION'
                GROUP BY entity_ref, scope_ref
            ),
            current_reaffirmations AS (
                SELECT 
                    d.entity_ref,
                    d.scope_ref,
                    d.classification,
                    d.declared_at,
                    d.declaration_id,
                    lr.last_recl_id
                FROM state__declarations d
                LEFT JOIN last_reclassification lr
                    ON d.entity_ref = lr.entity_ref
                    AND d.scope_ref = lr.scope_ref
                WHERE d.declaration_kind = 'REAFFIRMATION'
                    AND (lr.last_recl_id IS NULL OR d.declaration_id > lr.last_recl_id)
            )
            SELECT 
                entity_ref,
                scope_ref,
                classification,
                COUNT(*) as consecutive_reaffirmations,
                MIN(declared_at) as first_reaffirmed_at,
                MAX(declared_at) as last_reaffirmed_at
            FROM current_reaffirmations
            GROUP BY entity_ref, scope_ref, classification
            HAVING COUNT(*) > 1
            ORDER BY consecutive_reaffirmations DESC, entity_ref
        """)

        cursor.execute("""
            CREATE VIEW IF NOT EXISTS view_ops_unclosed_quotes AS
            SELECT 
                q.id,
                q.quote_id,
                q.final_quoted_price,
                q.lead_time_days,
                q.payment_terms_days,
                q.status,
                q.created_at,
                cu.name as customer_name,
                CAST((JULIANDAY('now') - JULIANDAY(q.created_at)) AS INTEGER) AS age_days
            FROM ops__quotes q
            LEFT JOIN ops__customers cu ON q.customer_id = cu.id
            LEFT JOIN ops__quote_outcome_events e ON q.id = e.quote_id AND e.outcome_type != 'NO_RESPONSE'
            WHERE e.id IS NULL
            ORDER BY q.created_at ASC
        """)

        cursor.execute("""
            CREATE VIEW IF NOT EXISTS view_state_time_in_state AS
            WITH latest AS (
                SELECT
                    entity_ref,
                    scope_ref,
                    MAX(declared_at) AS last_declared_at
                FROM state__declarations
                GROUP BY entity_ref, scope_ref
            ),
            latest_rows AS (
                SELECT d.*
                FROM state__declarations d
                JOIN latest l
                    ON d.entity_ref = l.entity_ref
                    AND d.scope_ref = l.scope_ref
                    AND d.declared_at = l.last_declared_at
            )
            SELECT
                e.entity_ref,
                e.entity_label,
                e.cadence_days,
                l.scope_ref,
                l.state_text,
                l.classification,
                l.declaration_kind,
                l.declared_by_actor_ref,
                l.declared_at,
                CAST((JULIANDAY('now') - JULIANDAY(l.declared_at)) AS INTEGER) AS days_since_declaration
            FROM state__entities e
            LEFT JOIN latest_rows l
                ON e.entity_ref = l.entity_ref
        """)
        
        print(f"[OK] State Ledger derived-state views created")
        
        conn.commit()
        conn.close()
        
        print(f"[SUCCESS] Database initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        raise


def verify_tables(db_path: Path) -> bool:
    """
    Verify core tables and views exist in database.
    
    Args:
        db_path: Path to database
    
    Returns:
        True if all required tables and views exist
    """
    print(f"\n[VERIFY] Checking core tables and views...")
    
    # Connect directly to verify
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Required tables
    required_tables = {
        'ops__': ['ops__quotes', 'ops__parts', 'ops__customers', 'ops__contacts'],
        'cutter__': ['cutter__events'],
        'state__': ['state__entities', 'state__recognition_owners', 'state__declarations']
    }
    
    # Required views (State Ledger derived states)
    required_views = [
        'view_ds1_persistent_continuity',
        'view_ds2_unowned_recognition',
        'view_ds5_deferred_recognition',
        'view_ops_unclosed_quotes',
        'view_state_time_in_state'
    ]
    
    all_objects = []
    missing_objects = []
    
    # Check tables
    for pattern, tables in required_tables.items():
        for table in tables:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table,))
            
            if cursor.fetchone():
                all_objects.append(table)
                print(f"  [OK] table: {table}")
            else:
                missing_objects.append(f"table:{table}")
                print(f"  [MISS] table: {table} (MISSING)")
    
    # Check views
    for view in required_views:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name=?
        """, (view,))
        
        if cursor.fetchone():
            all_objects.append(view)
            print(f"  [OK] view: {view}")
        else:
            missing_objects.append(f"view:{view}")
            print(f"  [MISS] view: {view} (MISSING)")
    
    conn.close()
    
    if missing_objects:
        print(f"\n[ERROR] Missing objects: {', '.join(missing_objects)}")
        return False
    
    print(f"\n[SUCCESS] All {len(all_objects)} required objects exist")
    print(f"  Tables: {len(sum(required_tables.values(), []))}")
    print(f"  Views: {len(required_views)}")
    return True


def print_summary(db_path: Path, backup_path: Path = None):
    """Print reset summary."""
    print("\n" + "="*70)
    print("DATABASE RESET COMPLETE")
    print("="*70)
    
    if backup_path:
        print(f"\nBackup: {backup_path}")
        backup_size = backup_path.stat().st_size / 1024
        print(f"  Size: {backup_size:.1f} KB")
    
    print(f"\nFresh DB: {db_path}")
    if db_path.exists():
        db_size = db_path.stat().st_size / 1024
        print(f"  Size: {db_size:.1f} KB")
    
    print("\nReady for:")
    print("  - Fresh quote data entry")
    print("  - State Ledger entity registration")
    print("  - Clean testing environment")
    
    print("\n" + "="*70)


def main():
    """Reset local database safely."""
    parser = argparse.ArgumentParser(
        description='Reset local database (backs up existing, creates fresh)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/reset_db.py
  python scripts/reset_db.py --db-path ./test.db

Safety:
  - Never deletes data (moves to backup)
  - Timestamped backups in ./data/backups/
  - Local dev only (do not use in production)
        """
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        help='Database path to reset (default: cutter.db or TEST_DB_PATH if set)'
    )
    
    args = parser.parse_args()
    
    # Respect TEST_DB_PATH for hermetic testing
    if args.db_path:
        db_path = Path(args.db_path)
    else:
        db_path = Path(os.environ.get('TEST_DB_PATH', 'cutter.db'))
    backup_dir = Path('data/backups')
    
    print("="*70)
    print("DATABASE RESET SCRIPT")
    print("="*70)
    print(f"\nTarget: {db_path}")
    print(f"Backup: {backup_dir}/")
    
    # Step 1: Backup existing
    backup_path = backup_existing_db(db_path, backup_dir)
    
    # Step 2: Create fresh
    create_fresh_db(db_path)
    
    # Step 3: Verify
    if not verify_tables(db_path):
        print("\n[ERROR] Table verification failed")
        return 1
    
    # Step 4: Summary
    print_summary(db_path, backup_path)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
