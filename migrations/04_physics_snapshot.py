"""
Migration 04: Add physics_snapshot_json to quotes table
Date: 2026-01-02
Purpose: Store raw cost breakdown (Material, Labor, Setup, Scrap) at quote time
         to prevent historical drift when pricing algorithms evolve.
"""
import sqlite3
import os

def migrate():
    """Add physics_snapshot_json column to quotes table."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'cutter.db')
    
    if not os.path.exists(db_path):
        print(f"[MIGRATION 04] Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Enable WAL mode
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(quotes);")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'physics_snapshot_json' in columns:
            print("[MIGRATION 04] Column 'physics_snapshot_json' already exists. Skipping.")
            conn.close()
            return
        
        # Add the column (TEXT type, allows NULL for historical quotes)
        print("[MIGRATION 04] Adding 'physics_snapshot_json' column to quotes table...")
        cursor.execute("""
            ALTER TABLE ops__quotes ADD COLUMN physics_snapshot_json TEXT;
        """)
        
        conn.commit()
        print("[MIGRATION 04] SUCCESS - Migration complete")
        
        # Verify
        cursor.execute("PRAGMA table_info(quotes);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"[MIGRATION 04] Current columns: {columns}")
        
    except Exception as e:
        print(f"[MIGRATION 04] ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()

