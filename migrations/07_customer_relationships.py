"""
Migration 07: Customer Relationships (Junction Tables)
Purpose: Support many-to-many relationships for parts and multi-company contacts
Date: January 6, 2026
"""

import sqlite3
import sys
import os

# Add parent directory to path for database.py import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

def migrate():
    """Add junction tables for customer relationships"""
    conn = database.get_connection()
    cursor = conn.cursor()
    
    print("[MIGRATION 07] Customer Relationships")
    print("=" * 50)
    
    try:
        # 1. customer_parts junction (many-to-many: customers <-> parts)
        print("\n[STEP 1] Creating customer_parts junction table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                genesis_hash TEXT NOT NULL,
                first_quoted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_quotes INTEGER DEFAULT 1,
                FOREIGN KEY (customer_id) REFERENCES ops__customers(id),
                UNIQUE(customer_id, genesis_hash)
            )
        """)
        print("    [OK] customer_parts table created")
        
        # 2. contact_companies junction (support contacts at multiple companies)
        print("\n[STEP 2] Creating contact_companies junction table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                is_primary BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES ops__contacts(id),
                FOREIGN KEY (customer_id) REFERENCES ops__customers(id),
                UNIQUE(contact_id, customer_id)
            )
        """)
        print("    [OK] contact_companies table created")
        
        # 3. Migrate existing contact->customer relationships to junction table
        print("\n[STEP 3] Migrating existing contact relationships...")
        cursor.execute("""
            INSERT OR IGNORE INTO contact_companies (contact_id, customer_id, is_primary)
            SELECT id, current_customer_id, 1
            FROM ops__contacts
            WHERE current_customer_id IS NOT NULL
        """)
        migrated = cursor.rowcount
        print(f"    [OK] Migrated {migrated} existing contact relationships")
        
        # 4. Populate customer_parts from existing quotes
        print("\n[STEP 4] Populating customer_parts from quote history...")
        cursor.execute("""
            INSERT OR IGNORE INTO customer_parts (customer_id, genesis_hash, first_quoted_at, total_quotes)
            SELECT 
                q.customer_id,
                p.genesis_hash,
                MIN(q.created_at) as first_quoted_at,
                COUNT(*) as total_quotes
            FROM ops__quotes q
            JOIN ops__parts p ON q.part_id = p.id
            WHERE q.customer_id IS NOT NULL 
              AND p.genesis_hash IS NOT NULL
            GROUP BY q.customer_id, p.genesis_hash
        """)
        parts_linked = cursor.rowcount
        print(f"    [OK] Linked {parts_linked} customer-part relationships")
        
        # 5. Create indices for performance
        print("\n[STEP 5] Creating indices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_parts_customer ON customer_parts(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_parts_hash ON customer_parts(genesis_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contact_companies_contact ON contact_companies(contact_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contact_companies_customer ON contact_companies(customer_id)")
        print("    [OK] Indices created")
        
        conn.commit()
        
        print("\n" + "=" * 50)
        print("[SUCCESS] Migration 07 complete!")
        print(f"   - customer_parts: {parts_linked} relationships")
        print(f"   - contact_companies: {migrated} relationships")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

