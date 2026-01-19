"""
Migration 08: Operational Events (Ledger Core)

PURPOSE: Create append-only operational_events table for Cutter ledger.
CONSTITUTIONAL AUTHORITY: Cutter — Canon.md (C4: Irreversible Memory, C7: Overrides Must Leave Scars)

DESIGN CONSTRAINTS:
- Append-only at DB level (trigger prevents UPDATE/DELETE)
- Event vocabulary is descriptive, never evaluative
- Time is first-class (created_at preserved)
- No retroactive edits allowed

DATE: 2026-01-09
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("cutter.db")

def migrate():
    """Apply migration: Create operational_events table with append-only constraints."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[MIGRATION 08] Creating operational_events table...")
    
    # Create operational_events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operational_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            quote_id INTEGER,
            event_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(quote_id) REFERENCES ops__quotes(id) ON DELETE RESTRICT
        )
    """)
    
    # Create index for query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_quote_id ON operational_events(quote_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_type ON operational_events(event_type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_created_at ON operational_events(created_at)
    """)
    
    # CRITICAL: Add trigger to enforce append-only constraint
    # Prevents UPDATE operations (C4: Irreversible Memory)
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS prevent_event_updates
        BEFORE UPDATE ON operational_events
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: Operational events are append-only (C4: Irreversible Memory)');
        END
    """)
    
    # CRITICAL: Add trigger to prevent DELETE operations
    # (C7: Overrides Must Leave Scars)
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS prevent_event_deletes
        BEFORE DELETE ON operational_events
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: Operational events cannot be deleted (C7: Overrides Must Leave Scars)');
        END
    """)
    
    conn.commit()
    conn.close()
    
    print("[MIGRATION 08] SUCCESS: operational_events table created with append-only constraints")
    print("[MIGRATION 08] SUCCESS: Triggers installed: prevent_event_updates, prevent_event_deletes")


def rollback():
    """
    Rollback migration.
    
    NOTE: This violates the Constitution (C4: Irreversible Memory).
    Only permitted during development before production deployment.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[MIGRATION 08 ROLLBACK] Dropping triggers and table...")
    
    cursor.execute("DROP TRIGGER IF EXISTS prevent_event_updates")
    cursor.execute("DROP TRIGGER IF EXISTS prevent_event_deletes")
    cursor.execute("DROP INDEX IF EXISTS idx_events_quote_id")
    cursor.execute("DROP INDEX IF EXISTS idx_events_type")
    cursor.execute("DROP INDEX IF EXISTS idx_events_created_at")
    cursor.execute("DROP TABLE IF EXISTS operational_events")
    
    conn.commit()
    conn.close()
    
    print("[MIGRATION 08 ROLLBACK] SUCCESS: Rolled back")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback()
    else:
        migrate()
