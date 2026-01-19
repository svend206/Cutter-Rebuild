"""
Migration 14: Add classification column to state__declarations

Adds nullable classification column that was removed during Phase 5e
but is still referenced by query code.

Context:
- Phase 5e (migration 13) replaced classification with declaration_kind
- However, classification was completely removed from schema
- Query code (get_declarations) still references classification
- This migration adds it back as nullable for backward compatibility

Constitutional Authority:
- No inference (NULL is correct, do not backfill)
- Append-only triggers preserved
- Optional field (nullable)
"""

import sqlite3
import shutil
from pathlib import Path


DB_PATH = Path("cutter.db")
BACKUP_SUFFIX = ".backup.pre-migration14"


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
    """Execute Migration 14: Add classification column."""
    print("\n" + "=" * 80)
    print("MIGRATION 14: Add classification Column to state__declarations")
    print("=" * 80)
    
    # Step 1: Backup
    print("\n[STEP 1] Backup Safety Check")
    backup_path = verify_or_create_backup()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Step 2: Check if column already exists
    print("\n[STEP 2] Check Current Schema")
    cursor.execute("PRAGMA table_info(state__declarations)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'classification' in columns:
        print("[SKIP] classification column already exists")
        conn.close()
        return
    
    print("[OK] classification column not present (will add)")
    
    # Step 3: Add classification column
    print("\n[STEP 3] Add classification Column")
    print("  Adding as nullable TEXT column (no default, no backfill)")
    
    cursor.execute("""
        ALTER TABLE state__declarations
        ADD COLUMN classification TEXT
    """)
    
    print("[OK] classification column added")
    print("  - Type: TEXT")
    print("  - Nullable: YES")
    print("  - Default: NULL")
    print("  - Backfill: NONE (NULL is correct)")
    
    conn.commit()
    
    # Step 4: Verify column added
    print("\n[STEP 4] Verify Column Added")
    cursor.execute("PRAGMA table_info(state__declarations)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    if 'classification' not in columns:
        raise RuntimeError("classification column not found after ALTER TABLE")
    
    print(f"[OK] classification column exists: {columns['classification']}")
    
    # Step 5: Verify triggers still active
    print("\n[STEP 5] Verify Append-Only Triggers")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='trigger' AND tbl_name='state__declarations'
    """)
    triggers = [row[0] for row in cursor.fetchall()]
    
    required_triggers = [
        'block_state_declarations_update',
        'block_state_declarations_delete'
    ]
    
    for trigger in required_triggers:
        if trigger in triggers:
            print(f"[OK] Trigger active: {trigger}")
        else:
            print(f"[WARNING] Trigger missing: {trigger}")
    
    # Step 6: Test append-only enforcement
    print("\n[STEP 6] Test Append-Only Enforcement")
    cursor.execute("""
        SELECT declaration_id FROM state__declarations LIMIT 1
    """)
    test_row = cursor.fetchone()
    
    if test_row:
        test_id = test_row[0]
        try:
            cursor.execute(f"""
                UPDATE state__declarations 
                SET classification = 'test' 
                WHERE declaration_id = {test_id}
            """)
            print("[ERROR] UPDATE trigger did NOT block modification!")
            conn.rollback()
            raise RuntimeError("Append-only trigger not working")
        except sqlite3.IntegrityError as e:
            if 'Constitutional violation' in str(e) or 'append-only' in str(e):
                print("[OK] UPDATE trigger blocked (append-only enforced)")
            else:
                raise
    else:
        print("[SKIP] No rows to test (empty table)")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("[SUCCESS] Migration 14 Complete")
    print("=" * 80)
    print()
    print("Added:")
    print("  - classification column (TEXT, nullable)")
    print()
    print("Preserved:")
    print("  - Append-only triggers (UPDATE/DELETE blocked)")
    print("  - All existing data (no backfill)")
    print("  - declaration_kind column (unchanged)")
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
        print("Rollback available: python migrations/14_add_classification_column.py rollback")
        exit(1)
