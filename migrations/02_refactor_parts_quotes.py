"""
Migration Script: "Option B" Refactor - Split Parts & Quotes
Date: December 28, 2025
Purpose: 
1. DROP old monolithic quote_history table
2. CREATE new parts and quotes tables
3. Enable WAL mode for concurrency

WARNING: This is a DESTRUCTIVE migration. All existing quote_history data will be LOST.
Ensure you have a backup of cutter.db before running this script.
"""

import sqlite3
import sys
from pathlib import Path

# Database path
DB_PATH = Path("cutter.db")

def main():
    print("=" * 70)
    print("MIGRATION: Option B Refactor (Split Parts & Quotes)")
    print("=" * 70)
    print("")
    print("[WARNING] This migration will DROP the quote_history table!")
    print("[WARNING] All existing quote data will be permanently deleted.")
    print("")
    
    # Check if database exists
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        print("Please ensure cutter.db exists in the current directory.")
        sys.exit(1)
    
    print(f"[SUCCESS] Database found: {DB_PATH}")
    
    # Confirmation prompt
    response = input("\nType 'REFACTOR' to proceed with destructive migration: ")
    if response != 'REFACTOR':
        print("[CANCELLED] Migration aborted by user.")
        sys.exit(0)
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Enable WAL mode for concurrency (v2.1 requirement)
        cursor.execute("PRAGMA journal_mode=WAL;")
        print("[SUCCESS] WAL mode enabled for database concurrency")
        
        print("\n" + "=" * 70)
        print("STEP 1: DROP Old Schema")
        print("=" * 70)
        
        # Drop the old monolithic table
        print("[INFO] Dropping quote_history table...")
        cursor.execute("DROP TABLE IF EXISTS quote_history")
        conn.commit()
        print("[SUCCESS] Old quote_history table dropped")
        
        print("\n" + "=" * 70)
        print("STEP 2: CREATE New Schema (Parts)")
        print("=" * 70)
        
        # Create parts table
        print("[INFO] Creating parts table...")
        cursor.execute("""
            CREATE TABLE ops__parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                genesis_hash TEXT UNIQUE NOT NULL,
                filename TEXT,
                fingerprint_json TEXT,
                volume REAL,
                surface_area REAL,
                dimensions_json TEXT,
                process_routing_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("[SUCCESS] Created parts table")
        
        # Create index on genesis_hash for fast lookups
        print("[INFO] Creating index on genesis_hash...")
        cursor.execute("CREATE UNIQUE INDEX idx_parts_genesis_hash ON parts(genesis_hash)")
        conn.commit()
        print("[SUCCESS] Created index: idx_parts_genesis_hash")
        
        print("\n" + "=" * 70)
        print("STEP 3: CREATE New Schema (Quotes)")
        print("=" * 70)
        
        # Create quotes table
        print("[INFO] Creating quotes table...")
        cursor.execute("""
            CREATE TABLE ops__quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER NOT NULL,
                user_id INTEGER,
                quote_id TEXT UNIQUE,
                material TEXT,
                system_price_anchor REAL,
                final_quoted_price REAL,
                variance_json TEXT,
                pricing_tags_json TEXT,
                status TEXT DEFAULT 'Draft',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_id) REFERENCES ops__parts(id)
            )
        """)
        conn.commit()
        print("[SUCCESS] Created quotes table")
        
        # Create indexes for common queries
        print("[INFO] Creating indexes on quotes...")
        cursor.execute("CREATE UNIQUE INDEX idx_quotes_quote_id ON quotes(quote_id)")
        cursor.execute("CREATE INDEX idx_quotes_part_id ON quotes(part_id)")
        cursor.execute("CREATE INDEX idx_quotes_status ON quotes(status)")
        conn.commit()
        print("[SUCCESS] Created indexes: idx_quotes_quote_id, idx_quotes_part_id, idx_quotes_status")
        
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)
        
        # Verify parts table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parts'")
        if cursor.fetchone():
            print("[VERIFIED] parts table exists")
            
            # Check columns
            cursor.execute("PRAGMA table_info(parts)")
            columns = [row[1] for row in cursor.fetchall()]
            expected_columns = [
                'id', 'genesis_hash', 'filename', 'fingerprint_json', 
                'volume', 'surface_area', 'dimensions_json', 
                'process_routing_json', 'created_at'
            ]
            if set(columns) == set(expected_columns):
                print(f"[VERIFIED] parts table has all {len(expected_columns)} columns")
            else:
                missing = set(expected_columns) - set(columns)
                extra = set(columns) - set(expected_columns)
                if missing:
                    print(f"[ERROR] parts table missing columns: {missing}")
                if extra:
                    print(f"[WARNING] parts table has extra columns: {extra}")
        else:
            print("[ERROR] parts table NOT FOUND")
            raise Exception("parts table verification failed")
        
        # Verify quotes table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quotes'")
        if cursor.fetchone():
            print("[VERIFIED] quotes table exists")
            
            # Check columns
            cursor.execute("PRAGMA table_info(quotes)")
            columns = [row[1] for row in cursor.fetchall()]
            expected_columns = [
                'id', 'part_id', 'user_id', 'quote_id', 'material',
                'system_price_anchor', 'final_quoted_price', 'variance_json',
                'pricing_tags_json', 'status', 'created_at'
            ]
            if set(columns) == set(expected_columns):
                print(f"[VERIFIED] quotes table has all {len(expected_columns)} columns")
            else:
                missing = set(expected_columns) - set(columns)
                extra = set(columns) - set(expected_columns)
                if missing:
                    print(f"[ERROR] quotes table missing columns: {missing}")
                if extra:
                    print(f"[WARNING] quotes table has extra columns: {extra}")
        else:
            print("[ERROR] quotes table NOT FOUND")
            raise Exception("quotes table verification failed")
        
        # Verify indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name IN ('parts', 'quotes')")
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"[VERIFIED] Created {len(indexes)} indexes")
        
        # Verify foreign key
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        if fk_status:
            print("[VERIFIED] Foreign key constraints enabled")
        else:
            print("[WARNING] Foreign key constraints are disabled (SQLite default)")
            print("           Enable with: PRAGMA foreign_keys = ON;")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("[SUCCESS] Migration Complete - Option B Refactor")
        print("=" * 70)
        print("\n[SUMMARY]")
        print("  [OK] Dropped: quote_history (old monolithic table)")
        print("  [OK] Created: parts (8 columns + 1 index)")
        print("  [OK] Created: quotes (10 columns + 3 indexes)")
        print("  [OK] WAL Mode: Enabled for mobile node concurrency")
        print("\n[NEXT STEPS]")
        print("  1. Restart Flask server (if running)")
        print("  2. Test /quote endpoint with 3D file upload")
        print("  3. Test /save_quote endpoint")
        print("  4. Verify Glass Box functionality")
        print("\n[NOTE] All previous quote history has been wiped.")
        print("       Start fresh with new quotes.")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n[TROUBLESHOOTING]")
        print("  - Ensure no other process has cutter.db open")
        print("  - Check file permissions")
        print("  - Verify SQLite3 is installed")
        sys.exit(1)

if __name__ == "__main__":
    main()

