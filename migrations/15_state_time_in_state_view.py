"""
Migration 15: State Ledger Time-in-State View

Adds a derived view that exposes last declaration per entity/scope
and elapsed time since declaration without inference.
"""

import sqlite3
from pathlib import Path


DB_PATH = Path("cutter.db")


def migrate() -> None:
    print("\n" + "=" * 80)
    print("MIGRATION 15: State Ledger Time-in-State View")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()

    print("[OK] Created view_state_time_in_state")
    print("[SUCCESS] Migration 15 Complete")


if __name__ == "__main__":
    migrate()
