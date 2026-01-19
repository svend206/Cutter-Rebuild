"""
Migration 11: Phase 4d - Industry-Agnostic Cutter Ledger Storage

Replace domain-coupled quote_id column with industry-agnostic subject_ref TEXT.
Preserves all existing events and append-only enforcement.

Changes:
- Create new cutter__events table with subject_ref TEXT (no FK)
- Copy all rows from cutter__operational_events with mapping:
  subject_ref = CASE WHEN quote_id IS NULL THEN 'unknown' ELSE 'quote:' || quote_id END
- Recreate append-only triggers (block UPDATE/DELETE)
- Rename old table to cutter__operational_events__legacy_4d
- Create VIEW cutter__operational_events for backward compatibility

Constitutional Authority: 
- C2 (Outcome Agnosticism): Remove domain coupling from ledger
- C4 (Irreversible Memory): Preserve append-only enforcement
- C7 (Overrides Must Leave Scars): Maintain complete history
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


DB_PATH = Path("cutter.db")
BACKUP_SUFFIX = ".backup.pre-phase4d"


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
    """Execute Phase 4d migration to industry-agnostic subject_ref."""
    print("\n" + "=" * 80)
    print("MIGRATION 11: Phase 4d - Industry-Agnostic Cutter Ledger")
    print("=" * 80)
    
    # Step 1: Backup safety check
    print("\n[STEP 1] Backup Safety Check")
    backup_path = verify_or_create_backup()
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF;")  # Disable FKs during migration
    cursor = conn.cursor()
    
    # Step 2: Verify source table exists
    print("\n[STEP 2] Verify Source Table")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='cutter__operational_events'
    """)
    if not cursor.fetchone():
        raise RuntimeError("Source table cutter__operational_events not found")
    print("[OK] Source table exists")
    
    # Count rows to migrate
    cursor.execute("SELECT COUNT(*) FROM cutter__operational_events")
    row_count = cursor.fetchone()[0]
    print(f"[OK] Found {row_count} events to migrate")
    
    # Step 3: Create new cutter__events table
    print("\n[STEP 3] Create New Industry-Agnostic Table")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cutter__events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            subject_ref TEXT NOT NULL,
            event_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            ingested_by_service TEXT,
            ingested_by_version TEXT
        )
    """)
    print("[OK] Created cutter__events table")
    
    # Step 4: Copy all rows with subject_ref mapping
    print("\n[STEP 4] Copy Events with subject_ref Mapping")
    print("  Mapping: quote_id -> 'quote:{id}' | NULL -> 'unknown'")
    
    cursor.execute("""
        INSERT INTO cutter__events (
            id, event_type, subject_ref, event_data, 
            created_at, ingested_by_service, ingested_by_version
        )
        SELECT 
            id,
            event_type,
            CASE 
                WHEN quote_id IS NULL THEN 'unknown'
                ELSE 'quote:' || quote_id
            END as subject_ref,
            event_data,
            created_at,
            ingested_by_service,
            ingested_by_version
        FROM cutter__operational_events
    """)
    
    migrated_count = cursor.rowcount
    print(f"[OK] Migrated {migrated_count} events")
    
    # Verify row count matches
    cursor.execute("SELECT COUNT(*) FROM cutter__events")
    new_count = cursor.fetchone()[0]
    assert new_count == row_count, f"Row count mismatch: expected {row_count}, got {new_count}"
    print(f"[VERIFY] Row count matches: {new_count}")
    
    # Step 5: Create indexes on new table
    print("\n[STEP 5] Create Indexes")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_subject_ref 
        ON cutter__events(subject_ref)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_type 
        ON cutter__events(event_type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_created_at 
        ON cutter__events(created_at)
    """)
    print("[OK] Created indexes on cutter__events")
    
    # Step 6: Recreate append-only triggers
    print("\n[STEP 6] Recreate Append-Only Triggers")
    cursor.execute("""
        CREATE TRIGGER prevent_events_updates
        BEFORE UPDATE ON cutter__events
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: Cutter Ledger is append-only (C4: Irreversible Memory)');
        END
    """)
    print("[OK] Created UPDATE blocker trigger")
    
    cursor.execute("""
        CREATE TRIGGER prevent_events_deletes
        BEFORE DELETE ON cutter__events
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: Cutter Ledger cannot be deleted (C7: Overrides Must Leave Scars)');
        END
    """)
    print("[OK] Created DELETE blocker trigger")
    
    # Verify triggers work
    try:
        cursor.execute("UPDATE cutter__events SET event_type = 'TEST' WHERE id = 1")
        raise RuntimeError("UPDATE trigger failed to block")
    except sqlite3.IntegrityError as e:
        if 'Constitutional violation' in str(e):
            print("[VERIFY] UPDATE trigger active")
        else:
            raise
    
    try:
        cursor.execute("DELETE FROM cutter__events WHERE id = 1")
        raise RuntimeError("DELETE trigger failed to block")
    except sqlite3.IntegrityError as e:
        if 'Constitutional violation' in str(e):
            print("[VERIFY] DELETE trigger active")
        else:
            raise
    
    # Step 7: Drop old triggers
    print("\n[STEP 7] Drop Old Triggers")
    cursor.execute("DROP TRIGGER IF EXISTS prevent_event_updates")
    cursor.execute("DROP TRIGGER IF EXISTS prevent_event_deletes")
    print("[OK] Dropped old triggers from cutter__operational_events")
    
    # Step 8: Rename old table to legacy
    print("\n[STEP 8] Rename Old Table to Legacy")
    cursor.execute("""
        ALTER TABLE cutter__operational_events 
        RENAME TO cutter__operational_events__legacy_4d
    """)
    print("[OK] Renamed to cutter__operational_events__legacy_4d")
    
    # Step 9: Create backward compatibility VIEW
    print("\n[STEP 9] Create Backward Compatibility View")
    cursor.execute("""
        CREATE VIEW cutter__operational_events AS
        SELECT 
            id,
            event_type,
            CASE 
                WHEN subject_ref LIKE 'quote:%' THEN 
                    CAST(SUBSTR(subject_ref, 7) AS INTEGER)
                ELSE NULL 
            END as quote_id,
            subject_ref,
            event_data,
            created_at,
            ingested_by_service,
            ingested_by_version
        FROM cutter__events
    """)
    print("[OK] Created VIEW cutter__operational_events")
    print("  Exposes computed quote_id for backward compatibility")
    print("  Writes should go directly to cutter__events")
    
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON;")  # Re-enable FKs
    
    # Step 10: Final verification
    print("\n[STEP 10] Final Verification")
    cursor.execute("SELECT COUNT(*) FROM cutter__events")
    final_count = cursor.fetchone()[0]
    print(f"[OK] cutter__events: {final_count} rows")
    
    cursor.execute("SELECT COUNT(*) FROM cutter__operational_events__legacy_4d")
    legacy_count = cursor.fetchone()[0]
    print(f"[OK] legacy table: {legacy_count} rows")
    
    cursor.execute("SELECT COUNT(*) FROM cutter__operational_events")
    view_count = cursor.fetchone()[0]
    print(f"[OK] view: {view_count} rows")
    
    assert final_count == legacy_count == view_count, "Row count mismatch after migration"
    
    # Sample subject_ref values
    cursor.execute("SELECT DISTINCT subject_ref FROM cutter__events LIMIT 5")
    samples = cursor.fetchall()
    print(f"[VERIFY] Sample subject_ref values: {[s[0] for s in samples]}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("[SUCCESS] Migration 11 Complete: Industry-Agnostic Cutter Ledger")
    print("=" * 80)
    print()
    print("Changes:")
    print(f"  - Migrated {final_count} events to cutter__events")
    print("  - subject_ref column replaces quote_id (domain-agnostic)")
    print("  - Append-only triggers active on new table")
    print("  - Legacy table preserved as cutter__operational_events__legacy_4d")
    print("  - Backward compatibility view created")
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
        print("Rollback available: python migrations/11_phase4d_subject_ref.py rollback")
        exit(1)
