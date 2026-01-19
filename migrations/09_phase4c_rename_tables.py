"""
Migration 09: Phase 4C Table Rename

PURPOSE: Rename all database tables with layer-based prefixes (ops__, cutter__).
CONSTITUTIONAL AUTHORITY: PHASE_4C_RENAME_PLAN.md (approved 2026-01-11)
INVARIANT: NO BEHAVIOR CHANGE - only table names are modified.

SCOPE:
- 10 tables → ops__ prefix (Operating Layer)
- 1 table → cutter__ prefix (Cutter Ledger)

DATE: 2026-01-11
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("cutter.db")


def migrate():
    """Apply migration: Rename all tables per approved Phase 4C plan."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[MIGRATION 09] Phase 4C: Renaming tables with layer prefixes...")
    print("[INVARIANT] NO BEHAVIOR CHANGE - only table names modified")
    print()
    
    # Helper function to safely rename table (skip if already renamed)
    def safe_rename(old_name, new_name):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (old_name,))
        if cursor.fetchone():
            cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
            print(f"  [OK] {old_name} -> {new_name}")
            return True
        else:
            print(f"  [SKIP] {old_name} (already renamed or doesn't exist)")
            return False
    
    # Step 1: Rename Leaf Tables (No Dependencies)
    print("Step 1: Renaming leaf tables...")
    
    safe_rename("materials", "ops__materials")
    safe_rename("shop_config", "ops__shop_config")
    safe_rename("custom_tags", "ops__custom_tags")
    safe_rename("guild_ledger", "ops__guild_ledger")
    print()
    
    # Step 2: Rename Identity Tables
    print("Step 2: Renaming identity tables...")
    
    safe_rename("customers", "ops__customers")
    safe_rename("parts", "ops__parts")
    safe_rename("contacts", "ops__contacts")
    print()
    
    # Step 3: Rename Transaction Table
    print("Step 3: Renaming transaction table...")
    
    safe_rename("quotes", "ops__quotes")
    print()
    
    # Step 4: Rename Event Tables
    print("Step 4: Renaming event tables...")
    
    safe_rename("operational_events", "cutter__operational_events")
    safe_rename("quote_outcome_events", "ops__quote_outcome_events")
    print()
    
    # Step 5: Rename Legacy Table
    print("Step 5: Renaming legacy table...")
    
    safe_rename("quote_history", "ops__quote_history")
    print()
    
    # Commit all changes
    conn.commit()
    
    # Verification
    print("Verifying table renames...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_ops = [
        'ops__contacts', 'ops__custom_tags', 'ops__customers', 'ops__guild_ledger',
        'ops__materials', 'ops__parts', 'ops__quote_history', 'ops__quote_outcome_events',
        'ops__quotes', 'ops__shop_config'
    ]
    expected_cutter = ['cutter__operational_events']
    
    # Check all new names exist
    for table in expected_ops + expected_cutter:
        if table not in tables:
            conn.close()
            raise AssertionError(f"ERROR: Table {table} not found after rename!")
    
    # Check old names don't exist
    old_names = [
        'contacts', 'custom_tags', 'customers', 'guild_ledger', 'materials',
        'operational_events', 'parts', 'quote_history', 'quote_outcome_events',
        'quotes', 'shop_config'
    ]
    for old_name in old_names:
        if old_name in tables:
            conn.close()
            raise AssertionError(f"ERROR: Old table name {old_name} still exists!")
    
    print(f"  [OK] All 10 ops__ tables verified")
    print(f"  [OK] All 1 cutter__ table verified")
    print(f"  [OK] No old table names remain")
    print()
    
    # Verify triggers on cutter__operational_events
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='trigger' AND tbl_name='cutter__operational_events'
    """)
    triggers = [row[0] for row in cursor.fetchall()]
    
    expected_triggers = ['prevent_event_updates', 'prevent_event_deletes']
    for trigger in expected_triggers:
        if trigger not in triggers:
            conn.close()
            raise AssertionError(f"ERROR: Trigger {trigger} not found on cutter__operational_events!")
    
    print(f"  [OK] Triggers verified on cutter__operational_events: {triggers}")
    print()
    
    conn.close()
    
    print("[MIGRATION 09] SUCCESS: All tables renamed with layer prefixes")
    print("[NEXT STEP] Update code references to use new table names")


def rollback():
    """
    Rollback migration: Restore original table names.
    
    NOTE: Only use this if code has NOT been updated yet.
    If code has been updated, use git revert instead.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[MIGRATION 09 ROLLBACK] Restoring original table names...")
    
    # Reverse all renames
    cursor.execute("ALTER TABLE ops__materials RENAME TO materials")
    cursor.execute("ALTER TABLE ops__shop_config RENAME TO shop_config")
    cursor.execute("ALTER TABLE ops__custom_tags RENAME TO custom_tags")
    cursor.execute("ALTER TABLE ops__guild_ledger RENAME TO guild_ledger")
    cursor.execute("ALTER TABLE ops__customers RENAME TO customers")
    cursor.execute("ALTER TABLE ops__parts RENAME TO parts")
    cursor.execute("ALTER TABLE ops__contacts RENAME TO contacts")
    cursor.execute("ALTER TABLE ops__quotes RENAME TO quotes")
    cursor.execute("ALTER TABLE cutter__operational_events RENAME TO operational_events")
    cursor.execute("ALTER TABLE ops__quote_outcome_events RENAME TO quote_outcome_events")
    cursor.execute("ALTER TABLE ops__quote_history RENAME TO quote_history")
    
    conn.commit()
    conn.close()
    
    print("[MIGRATION 09 ROLLBACK] SUCCESS: All tables restored to original names")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback()
    else:
        migrate()
