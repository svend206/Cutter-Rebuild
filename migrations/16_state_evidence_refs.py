"""
Migration 16: State Ledger Evidence References

Adds evidence_refs_json to state__declarations for inert evidence references.
"""

import sqlite3
from pathlib import Path


DB_PATH = Path("cutter.db")


def migrate() -> None:
    print("\n" + "=" * 80)
    print("MIGRATION 16: State Ledger Evidence References")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(state__declarations)")
    columns = [row[1] for row in cursor.fetchall()]

    if "evidence_refs_json" not in columns:
        cursor.execute("""
            ALTER TABLE state__declarations
            ADD COLUMN evidence_refs_json TEXT DEFAULT '[]'
        """)
        cursor.execute("""
            UPDATE state__declarations
            SET evidence_refs_json = '[]'
            WHERE evidence_refs_json IS NULL
        """)
        print("[OK] Added evidence_refs_json column")
    else:
        print("[SKIP] evidence_refs_json already exists")

    conn.commit()
    conn.close()

    print("[SUCCESS] Migration 16 Complete")


if __name__ == "__main__":
    migrate()
