"""
Migration 10: Deterministic Provenance for Cutter Ledger

Replace stack-based ingested_by with deterministic service/version tracking.

Changes:
- Add ingested_by_service (TEXT) - Service/app identifier
- Add ingested_by_version (TEXT) - Git SHA or version number
- Repurpose ingested_by for legacy compatibility (deprecated)

Constitutional Authority: C7 (Overrides Must Leave Scars) - Provenance tracking
"""

import sqlite3
from pathlib import Path


DB_PATH = Path("cutter.db")


def migrate():
    """Add deterministic provenance columns to cutter__operational_events."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[MIGRATION 10] Adding deterministic provenance columns...")
    
    # Add ingested_by_service column
    try:
        cursor.execute("""
            ALTER TABLE cutter__operational_events
            ADD COLUMN ingested_by_service TEXT
        """)
        print("[OK] Added ingested_by_service column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("[SKIP] ingested_by_service already exists")
        else:
            raise
    
    # Add ingested_by_version column
    try:
        cursor.execute("""
            ALTER TABLE cutter__operational_events
            ADD COLUMN ingested_by_version TEXT
        """)
        print("[OK] Added ingested_by_version column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("[SKIP] ingested_by_version already exists")
        else:
            raise
    
    conn.commit()
    
    # Verify schema
    cursor.execute("PRAGMA table_info(cutter__operational_events)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"[VERIFY] Columns: {columns}")
    
    assert 'ingested_by_service' in columns, "ingested_by_service not found"
    assert 'ingested_by_version' in columns, "ingested_by_version not found"
    
    conn.close()
    
    print("[MIGRATION 10] Complete: Deterministic provenance columns added")


if __name__ == '__main__':
    migrate()
