"""
Migration 13: Phase 5e - Explicit Declaration Kind

Fix DS-1 (Persistent Continuity) by adding explicit declaration_kind.

Problem:
- Current DS-1 cannot distinguish reaffirmation vs reclassification
- Claims "consecutive reaffirmations" without detecting consecutiveness
- Groups by classification but doesn't track declaration intent

Solution:
- Add declaration_kind column (REAFFIRMATION | RECLASSIFICATION)
- Backfill existing rows as RECLASSIFICATION (cannot assume continuity)
- Redefine DS-1 view to compute TRUE consecutive reaffirmation streaks

Constitutional Authority:
- C5 (Separation of Observation): No inference from state_text differences
- DS-1 (Persistent Continuity): Must be mechanically and truthfully detected
"""

import sqlite3
import shutil
from pathlib import Path


DB_PATH = Path("cutter.db")
BACKUP_SUFFIX = ".backup.pre-phase5e"


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
    """Execute Phase 5e migration: Add declaration_kind and fix DS-1."""
    print("\n" + "=" * 80)
    print("MIGRATION 13: Phase 5e - Explicit Declaration Kind")
    print("=" * 80)
    
    # Step 1: Backup safety check
    print("\n[STEP 1] Backup Safety Check")
    backup_path = verify_or_create_backup()
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    # Step 2: Add declaration_kind column
    print("\n[STEP 2] Add declaration_kind Column")
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(state__declarations)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'declaration_kind' in columns:
        print("[SKIP] declaration_kind column already exists")
    else:
        # SQLite doesn't support ALTER TABLE ADD COLUMN with CHECK constraint directly
        # We'll add column first, then create CHECK via trigger
        cursor.execute("""
            ALTER TABLE state__declarations
            ADD COLUMN declaration_kind TEXT
        """)
        print("[OK] Added declaration_kind column")
    
    # Step 3: Temporarily drop triggers for backfill
    print("\n[STEP 3] Drop Triggers (Temporary - for backfill)")
    cursor.execute("DROP TRIGGER IF EXISTS prevent_declaration_updates")
    cursor.execute("DROP TRIGGER IF EXISTS prevent_declaration_deletes")
    print("[OK] Dropped triggers temporarily")
    
    # Step 4: Backfill existing rows
    print("\n[STEP 4] Backfill Existing Declarations")
    print("  Strategy: Set all existing declarations to RECLASSIFICATION")
    print("  Rationale: Cannot assume they were reaffirmations without inference")
    
    cursor.execute("""
        SELECT COUNT(*) FROM state__declarations
        WHERE declaration_kind IS NULL
    """)
    null_count = cursor.fetchone()[0]
    
    if null_count > 0:
        cursor.execute("""
            UPDATE state__declarations
            SET declaration_kind = 'RECLASSIFICATION'
            WHERE declaration_kind IS NULL
        """)
        print(f"[OK] Backfilled {null_count} existing declarations as RECLASSIFICATION")
    else:
        print("[SKIP] No NULL declaration_kind values found")
    
    # Step 5: Make column NOT NULL and add CHECK constraint
    print("\n[STEP 5] Enforce declaration_kind Constraints")
    
    # Drop all views first (depend on table structure)
    cursor.execute("DROP VIEW IF EXISTS view_ds1_persistent_continuity")
    cursor.execute("DROP VIEW IF EXISTS view_ds2_unowned_recognition")
    cursor.execute("DROP VIEW IF EXISTS view_ds5_deferred_recognition")
    print("[OK] Dropped all derived state views")
    
    # SQLite doesn't support ALTER TABLE to add constraints
    # We need to recreate the table with the constraint
    print("  Recreating table with declaration_kind constraints...")
    
    # Create new table with constraint
    cursor.execute("""
        CREATE TABLE state__declarations_new (
            declaration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_ref TEXT NOT NULL,
            scope_ref TEXT NOT NULL,
            state_text TEXT NOT NULL,
            classification TEXT,
            declared_by_actor_ref TEXT NOT NULL,
            declared_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            supersedes_declaration_id INTEGER,
            cutter_evidence_ref TEXT,
            declaration_kind TEXT NOT NULL
                CHECK (declaration_kind IN ('REAFFIRMATION', 'RECLASSIFICATION')),
            FOREIGN KEY(entity_ref) REFERENCES state__entities(entity_ref) ON DELETE RESTRICT,
            FOREIGN KEY(supersedes_declaration_id) REFERENCES state__declarations(declaration_id)
        )
    """)
    print("[OK] Created new table with declaration_kind constraint")
    
    # Copy data from old table
    cursor.execute("""
        INSERT INTO state__declarations_new
        SELECT * FROM state__declarations
    """)
    print("[OK] Copied data to new table")
    
    # Drop old table
    cursor.execute("DROP TABLE state__declarations")
    print("[OK] Dropped old table")
    
    # Rename new table
    cursor.execute("ALTER TABLE state__declarations_new RENAME TO state__declarations")
    print("[OK] Renamed new table to state__declarations")
    
    # Recreate indexes
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
    print("[OK] Recreated indexes")
    
    # Recreate append-only triggers
    cursor.execute("""
        CREATE TRIGGER prevent_declaration_updates
        BEFORE UPDATE ON state__declarations
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: State declarations are append-only (C4: Irreversible Memory)');
        END
    """)
    cursor.execute("""
        CREATE TRIGGER prevent_declaration_deletes
        BEFORE DELETE ON state__declarations
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: State declarations cannot be deleted (DS: Explicit Recognition Only)');
        END
    """)
    print("[OK] Recreated append-only triggers")
    
    # Recreate DS-2 view
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
    print("[OK] Recreated view_ds2_unowned_recognition")
    
    # Recreate DS-5 view
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
    print("[OK] Recreated view_ds5_deferred_recognition")
    
    # Step 6: Create corrected DS-1 view
    print("\n[STEP 6] Create Corrected DS-1 View")
    print("  Detection: 2+ explicit reaffirmations since most recent reclassification")
    
    cursor.execute("""
        CREATE VIEW view_ds1_persistent_continuity AS
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
    print("[OK] Created corrected view_ds1_persistent_continuity")
    print("  Detects: 2+ explicit reaffirmations since last reclassification")
    print("  Threshold: HAVING COUNT(*) > 1 (avoids overclaiming on single reaffirmation)")
    
    conn.commit()
    
    # Step 7: Final verification
    print("\n[STEP 7] Final Verification")
    
    # Verify schema
    cursor.execute("PRAGMA table_info(state__declarations)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    assert 'declaration_kind' in columns, "declaration_kind column missing"
    print("[OK] declaration_kind column exists")
    
    # Verify no NULL values
    cursor.execute("""
        SELECT COUNT(*) FROM state__declarations
        WHERE declaration_kind IS NULL
    """)
    null_count = cursor.fetchone()[0]
    assert null_count == 0, f"Found {null_count} NULL declaration_kind values"
    print("[OK] No NULL declaration_kind values")
    
    # Verify constraint (try invalid value)
    try:
        cursor.execute("""
            INSERT INTO state__entities (entity_ref) 
            VALUES ('test:constraint')
        """)
        cursor.execute("""
            INSERT INTO state__declarations 
            (entity_ref, scope_ref, state_text, declared_by_actor_ref, declaration_kind)
            VALUES ('test:constraint', 'test', 'test', 'test:actor', 'INVALID')
        """)
        conn.rollback()
        raise RuntimeError("CHECK constraint failed to block invalid declaration_kind")
    except sqlite3.IntegrityError as e:
        if 'CHECK constraint' in str(e) or 'constraint failed' in str(e):
            print("[OK] CHECK constraint active (blocks invalid values)")
        else:
            raise
    
    # Verify view exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view' AND name='view_ds1_persistent_continuity'
    """)
    assert cursor.fetchone() is not None, "DS-1 view not found"
    print("[OK] view_ds1_persistent_continuity exists")
    
    # Count declarations by kind
    cursor.execute("""
        SELECT declaration_kind, COUNT(*) 
        FROM state__declarations 
        GROUP BY declaration_kind
    """)
    for kind, count in cursor.fetchall():
        print(f"[INFO] {kind}: {count} declarations")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("[SUCCESS] Migration 13 Complete: Explicit Declaration Kind")
    print("=" * 80)
    print()
    print("Changes:")
    print("  - Added declaration_kind column (REAFFIRMATION | RECLASSIFICATION)")
    print(f"  - Backfilled existing declarations as RECLASSIFICATION")
    print("  - Added CHECK constraint on declaration_kind")
    print("  - Recreated table with constraint")
    print("  - Recreated indexes and triggers")
    print("  - Fixed DS-1 view to detect TRUE consecutive reaffirmations")
    print()
    print("Constitutional Impact:")
    print("  - DS-1 now mechanically detects reaffirmation vs reclassification")
    print("  - No inference from state_text differences")
    print("  - Current continuity run properly computed (2+ reaffirmations since last reclassification)")
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
        print("Rollback available: python migrations/13_phase5e_declaration_kind.py rollback")
        exit(1)
