"""
Migration 17: Ops Unclosed Quotes View

Adds a derived view for quotes without outcomes with elapsed time.
"""

import sqlite3
from pathlib import Path


DB_PATH = Path("cutter.db")


def migrate() -> None:
    print("\n" + "=" * 80)
    print("MIGRATION 17: Ops Unclosed Quotes View")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()

    print("[OK] Created view_ops_unclosed_quotes")
    print("[SUCCESS] Migration 17 Complete")


if __name__ == "__main__":
    migrate()
