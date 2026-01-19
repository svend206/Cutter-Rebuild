"""
Migration 03: Rigorous 4-Table Identity Model

Purpose: Implement customers + contacts tables, add features_json to parts,
         recreate quotes table with proper foreign keys.

Date: December 30, 2025
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("cutter.db")

def get_connection():
    """Get database connection with WAL mode enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def check_table_exists(cursor, table_name):
    """Check if a table exists."""
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    return column_name in column_names

def main():
    print("=" * 70)
    print("MIGRATION 03: Rigorous 4-Table Identity Model")
    print("=" * 70)
    print("")
    print("[WARNING] This migration will:")
    print("  - CREATE customers table")
    print("  - CREATE contacts table")
    print("  - DROP and RECREATE quotes table (data will be lost)")
    print("  - ADD features_json to parts table")
    print("")
    print("Type 'IDENTITY' to proceed: ", end='')
    
    confirmation = input().strip()
    if confirmation != 'IDENTITY':
        print("[ABORTED] Migration cancelled by user")
        sys.exit(0)

    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        sys.exit(1)

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("[SUCCESS] Database found: cutter.db")
        print("[SUCCESS] WAL mode enabled")

        # --- STEP 1: ADD features_json TO parts TABLE ---
        print("\n" + "=" * 70)
        print("STEP 1: Upgrade parts table")
        print("=" * 70)
        
        if not check_table_exists(cursor, 'parts'):
            print("[ERROR] parts table does not exist. Run migration 02 first.")
            sys.exit(1)
        
        if not check_column_exists(cursor, 'parts', 'features_json'):
            print("[INFO] Adding features_json column to parts...")
            cursor.execute("ALTER TABLE ops__parts ADD COLUMN features_json TEXT")
            conn.commit()
            print("[SUCCESS] Added features_json to parts")
        else:
            print("[INFO] features_json already exists in parts")

        # --- STEP 2: CREATE customers TABLE ---
        print("\n" + "=" * 70)
        print("STEP 2: Create customers table")
        print("=" * 70)
        
        if check_table_exists(cursor, 'customers'):
            print("[INFO] customers table already exists, skipping creation")
        else:
            print("[INFO] Creating customers table...")
            cursor.execute("""
                CREATE TABLE ops__customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    domain TEXT NOT NULL,
                    corporate_tags_json TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX idx_customers_domain ON ops__customers (domain)")
            cursor.execute("CREATE INDEX idx_customers_name ON ops__customers (name)")
            conn.commit()
            print("[SUCCESS] Created customers table with indexes")

        # --- STEP 3: CREATE contacts TABLE ---
        print("\n" + "=" * 70)
        print("STEP 3: Create contacts table")
        print("=" * 70)
        
        if check_table_exists(cursor, 'contacts'):
            print("[INFO] contacts table already exists, skipping creation")
        else:
            print("[INFO] Creating contacts table...")
            cursor.execute("""
                CREATE TABLE ops__contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    behavior_tags_json TEXT,
                    current_customer_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (current_customer_id) REFERENCES ops__customers(id)
                )
            """)
            cursor.execute("CREATE INDEX idx_contacts_email ON ops__contacts (email)")
            cursor.execute("CREATE INDEX idx_contacts_customer ON ops__contacts (current_customer_id)")
            conn.commit()
            print("[SUCCESS] Created contacts table with indexes")

        # --- STEP 4: RECREATE quotes TABLE ---
        print("\n" + "=" * 70)
        print("STEP 4: Recreate quotes table with new schema")
        print("=" * 70)
        
        if check_table_exists(cursor, 'quotes'):
            print("[WARNING] Dropping existing quotes table (data will be lost)")
            cursor.execute("DROP TABLE ops__quotes")
            print("[SUCCESS] Dropped old quotes table")
        
        print("[INFO] Creating new quotes table with foreign keys...")
        cursor.execute("""
            CREATE TABLE ops__quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                contact_id INTEGER,
                user_id INTEGER,
                quote_id TEXT UNIQUE NOT NULL,
                material TEXT NOT NULL,
                pricing_tags_json TEXT,
                variance_json TEXT,
                final_quoted_price REAL NOT NULL,
                system_price_anchor REAL NOT NULL,
                quantity INTEGER DEFAULT 1,
                target_date TEXT,
                notes TEXT,
                status TEXT DEFAULT 'Draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_id) REFERENCES ops__parts(id) ON DELETE CASCADE,
                FOREIGN KEY (customer_id) REFERENCES ops__customers(id) ON DELETE RESTRICT,
                FOREIGN KEY (contact_id) REFERENCES ops__contacts(id) ON DELETE SET NULL
            )
        """)
        
        print("[INFO] Creating indexes on quotes...")
        cursor.execute("CREATE INDEX idx_quotes_quote_id ON quotes (quote_id)")
        cursor.execute("CREATE INDEX idx_quotes_part_id ON quotes (part_id)")
        cursor.execute("CREATE INDEX idx_quotes_customer_id ON quotes (customer_id)")
        cursor.execute("CREATE INDEX idx_quotes_status ON quotes (status)")
        conn.commit()
        print("[SUCCESS] Created quotes table with 4 indexes")

        # --- VERIFICATION ---
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)
        
        # Verify tables
        required_tables = ['parts', 'customers', 'contacts', 'quotes']
        for table in required_tables:
            if check_table_exists(cursor, table):
                print(f"[VERIFIED] {table} table exists")
            else:
                print(f"[ERROR] {table} table NOT FOUND")
                raise Exception(f"Verification failed for {table}")
        
        # Verify parts has features_json
        if check_column_exists(cursor, 'parts', 'features_json'):
            print("[VERIFIED] parts.features_json column exists")
        else:
            print("[ERROR] parts.features_json column NOT FOUND")
            raise Exception("features_json column missing from parts")
        
        # Verify quotes has new columns
        required_columns = [
            'customer_id', 'contact_id', 'quantity', 'target_date', 'notes'
        ]
        for col in required_columns:
            if check_column_exists(cursor, 'quotes', col):
                print(f"[VERIFIED] quotes.{col} column exists")
            else:
                print(f"[ERROR] quotes.{col} column NOT FOUND")
                raise Exception(f"{col} column missing from quotes")

        print("\n" + "=" * 70)
        print("[SUCCESS] Migration 03 Complete - 4-Table Identity Model")
        print("=" * 70)
        print("\n[SUMMARY]")
        print("  [OK] parts table upgraded (features_json added)")
        print("  [OK] customers table created (2 indexes)")
        print("  [OK] contacts table created (2 indexes)")
        print("  [OK] quotes table recreated with FKs (4 indexes)")
        print("\n[NEXT STEPS]")
        print("  1. Implement resolve_customer() in database.py")
        print("  2. Implement resolve_contact() in database.py")
        print("  3. Update create_quote() signature in database.py")
        print("  4. Update /save_quote endpoint in app.py")
        print("  5. Restart Flask server")
        print("\n[NOTE] All previous quote data has been wiped.")
        print("       Start fresh with new quotes using the 4-table model.")

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n[TROUBLESHOOTING]")
        print("  - Ensure Flask server is stopped")
        print("  - Ensure no other process has cutter.db open")
        print("  - Verify migration 02 was run successfully")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()

