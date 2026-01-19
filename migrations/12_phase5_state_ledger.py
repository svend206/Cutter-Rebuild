"""
Migration 12: Phase 5 - State Ledger

Create append-only State Ledger for explicit recognition declarations.

Tables:
- state__entities: Registry of entities that can have declared state
- state__recognition_owners: Enforces exactly one owner per entity
- state__declarations: Append-only ledger of explicit recognition

Constitutional Authority:
- DS-2 (Unowned Recognition): No committee recognition, ownerlessness detectable
- DS-5 (Deferred Recognition): Cadence tracking for recognition gaps
- C4 (Irreversible Memory): Append-only enforcement
- C5 (Separation of Observation and Judgment): No interpretation, only declaration
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


DB_PATH = Path("cutter.db")
BACKUP_SUFFIX = ".backup.pre-phase5"


def verify_or_create_backup():
    """Ensure database backup exists before migration."""
    backup_path = Path(str(DB_PATH) + BACKUP_SUFFIX)
    
    if backup_path.exists():
        print(f"[OK] Backup already exists: {backup_path}")
        return backup_path
    
    print(f"[BACKUP] Creating pre-migration backup: {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[OK] Backup created: {backup_path.stat().st_size} bytes")
    
    return backup_path


def migrate():
    """Execute Phase 5 migration: State Ledger tables and constraints."""
    print("\n" + "=" * 80)
    print("MIGRATION 12: Phase 5 - State Ledger")
    print("=" * 80)
    
    # Step 1: Backup safety check
    print("\n[STEP 1] Backup Safety Check")
    backup_path = verify_or_create_backup()
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    # Step 2: Create state__entities table
    print("\n[STEP 2] Create state__entities (Registry)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS state__entities (
            entity_ref TEXT PRIMARY KEY,
            entity_label TEXT,
            cadence_days INTEGER NOT NULL DEFAULT 7,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] Created state__entities table")
    print("  Format: entity_ref = '{type}:{id}' (e.g., 'company:1', 'customer:77')")
    print("  cadence_days: Expected reaffirmation cadence (default: 7 days)")
    
    # Step 3: Create state__recognition_owners table
    print("\n[STEP 3] Create state__recognition_owners (Ownership Tracking)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS state__recognition_owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_ref TEXT NOT NULL,
            owner_actor_ref TEXT NOT NULL,
            assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            unassigned_at TEXT,
            assigned_by_actor_ref TEXT NOT NULL,
            FOREIGN KEY(entity_ref) REFERENCES state__entities(entity_ref) ON DELETE RESTRICT
        )
    """)
    print("[OK] Created state__recognition_owners table")
    
    # Create unique constraint: exactly one current owner per entity
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_current_owner_per_entity
        ON state__recognition_owners(entity_ref)
        WHERE unassigned_at IS NULL
    """)
    print("[OK] Created unique constraint: one current owner per entity")
    print("  Enforcement: unassigned_at IS NULL must be unique per entity_ref")
    
    # Create index for ownership history queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ownership_history
        ON state__recognition_owners(entity_ref, assigned_at)
    """)
    print("[OK] Created index for ownership history")
    
    # Step 4: Create state__declarations table (append-only ledger)
    print("\n[STEP 4] Create state__declarations (Append-Only Ledger)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS state__declarations (
            declaration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_ref TEXT NOT NULL,
            scope_ref TEXT NOT NULL,
            state_text TEXT NOT NULL,
            classification TEXT,
            declared_by_actor_ref TEXT NOT NULL,
            declared_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            supersedes_declaration_id INTEGER,
            cutter_evidence_ref TEXT,
            FOREIGN KEY(entity_ref) REFERENCES state__entities(entity_ref) ON DELETE RESTRICT,
            FOREIGN KEY(supersedes_declaration_id) REFERENCES state__declarations(declaration_id)
        )
    """)
    print("[OK] Created state__declarations table")
    print("  Append-only: No UPDATE/DELETE allowed (enforced by triggers)")
    
    # Create indexes for common queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_declarations_entity
        ON state__declarations(entity_ref, declared_at DESC)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_declarations_scope
        ON state__declarations(scope_ref, declared_at DESC)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_declarations_actor
        ON state__declarations(declared_by_actor_ref, declared_at DESC)
    """)
    print("[OK] Created indexes on state__declarations")
    
    # Step 5: Create append-only triggers
    print("\n[STEP 5] Create Append-Only Triggers")
    cursor.execute("""
        CREATE TRIGGER prevent_declaration_updates
        BEFORE UPDATE ON state__declarations
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: State declarations are append-only (C4: Irreversible Memory)');
        END
    """)
    print("[OK] Created UPDATE blocker trigger")
    
    cursor.execute("""
        CREATE TRIGGER prevent_declaration_deletes
        BEFORE DELETE ON state__declarations
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: State declarations cannot be deleted (DS: Explicit Recognition Only)');
        END
    """)
    print("[OK] Created DELETE blocker trigger")
    
    # Verify triggers work
    print("[VERIFY] Testing append-only enforcement...")
    try:
        # Insert test declaration
        cursor.execute("""
            INSERT INTO state__entities (entity_ref, entity_label)
            VALUES ('test:migration', 'Migration Test Entity')
        """)
        cursor.execute("""
            INSERT INTO state__declarations 
            (entity_ref, scope_ref, state_text, declared_by_actor_ref)
            VALUES ('test:migration', 'test:scope', 'Test state', 'test:actor')
        """)
        test_id = cursor.lastrowid
        
        # Try UPDATE (should fail)
        try:
            cursor.execute(f"UPDATE state__declarations SET state_text = 'Modified' WHERE declaration_id = {test_id}")
            raise RuntimeError("UPDATE trigger failed to block")
        except sqlite3.IntegrityError as e:
            if 'Constitutional violation' in str(e):
                print("[VERIFY] UPDATE trigger active")
            else:
                raise
        
        # Try DELETE (should fail)
        try:
            cursor.execute(f"DELETE FROM state__declarations WHERE declaration_id = {test_id}")
            raise RuntimeError("DELETE trigger failed to block")
        except sqlite3.IntegrityError as e:
            if 'Constitutional violation' in str(e):
                print("[VERIFY] DELETE trigger active")
            else:
                raise
        
        # Note: Test data left in place (triggers work - DELETE is blocked!)
        # The test:migration entity demonstrates that triggers are active
        
    except Exception as e:
        print(f"[ERROR] Trigger verification failed: {e}")
        raise
    
    # Step 6: Create derived state views
    print("\n[STEP 6] Create Derived State Views")
    
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
    print("[OK] Created view_ds2_unowned_recognition")
    print("  Detects: Entities with no current recognition owner")
    
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
    print("[OK] Created view_ds5_deferred_recognition")
    print("  Detects: Entities past their cadence window (no recent declaration)")
    
    # DS-1: Persistent Continuity (optional, for when classification exists)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS view_ds1_persistent_continuity AS
        SELECT 
            entity_ref,
            scope_ref,
            classification,
            COUNT(*) as consecutive_reaffirmations,
            MIN(declared_at) as first_declaration,
            MAX(declared_at) as last_declaration
        FROM state__declarations
        WHERE classification IS NOT NULL
        GROUP BY entity_ref, scope_ref, classification
        HAVING COUNT(*) > 1
    """)
    print("[OK] Created view_ds1_persistent_continuity")
    print("  Detects: Consecutive reaffirmations without reclassification")
    
    conn.commit()
    
    # Step 7: Final verification
    print("\n[STEP 7] Final Verification")
    
    # Count tables
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='table' AND name LIKE 'state__%'
    """)
    table_count = cursor.fetchone()[0]
    print(f"[OK] Created {table_count} State Ledger tables")
    
    # Count views
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='view' AND name LIKE 'view_ds%'
    """)
    view_count = cursor.fetchone()[0]
    print(f"[OK] Created {view_count} derived state views")
    
    # Count triggers
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='trigger' AND tbl_name='state__declarations'
    """)
    trigger_count = cursor.fetchone()[0]
    print(f"[OK] Created {trigger_count} append-only triggers")
    
    # List all State Ledger objects
    cursor.execute("""
        SELECT type, name FROM sqlite_master 
        WHERE name LIKE 'state__%' OR name LIKE 'view_ds%'
        ORDER BY type, name
    """)
    objects = cursor.fetchall()
    print("\n[VERIFY] State Ledger objects created:")
    for obj_type, obj_name in objects:
        print(f"  {obj_type}: {obj_name}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("[SUCCESS] Migration 12 Complete: State Ledger")
    print("=" * 80)
    print()
    print("Created:")
    print(f"  - {table_count} tables (state__entities, state__recognition_owners, state__declarations)")
    print(f"  - {view_count} views (DS-2, DS-5, DS-1)")
    print(f"  - {trigger_count} triggers (append-only enforcement)")
    print()
    print("Constitutional Enforcement:")
    print("  - Append-only: UPDATE/DELETE blocked on state__declarations")
    print("  - Single owner: Unique constraint per entity (unassigned_at IS NULL)")
    print("  - Explicit recognition: No auto-generation, no inference")
    print("  - Structural visibility: DS-2 (unowned), DS-5 (deferred)")
    print()
    print(f"Backup: {backup_path}")
    print()


def rollback():
    """Rollback migration by restoring from backup."""
    backup_path = Path(str(DB_PATH) + BACKUP_SUFFIX)
    
    if not backup_path.exists():
        print("[ERROR] No backup found for rollback")
        return False
    
    print(f"[ROLLBACK] Restoring from {backup_path}")
    shutil.copy2(backup_path, DB_PATH)
    print("[OK] Database restored from backup")
    return True


if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"[ERROR] Migration failed: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        print()
        print("Rollback available: python migrations/12_phase5_state_ledger.py rollback")
        exit(1)
