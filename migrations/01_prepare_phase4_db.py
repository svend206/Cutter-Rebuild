"""
Migration Script: Prepare Database for Phase 4 (Glass Box & O-Score)
Date: December 28, 2025
Purpose: 
1. Seed pricing_tags table with "The Universal 9" tags
2. Add O-Score variance tracking columns to quote_history

This is a comprehensive Phase 4 database preparation script.
"""

import sqlite3
import sys
from pathlib import Path

# Database path
DB_PATH = Path("cutter.db")

def check_table_exists(cursor, table_name):
    """Check if a table exists in the database."""
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    return column_name in column_names

def is_table_empty(cursor, table_name):
    """Check if a table has any rows."""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    return count == 0

def main():
    print("=" * 70)
    print("MIGRATION: Prepare Database for Phase 4 (Glass Box & O-Score)")
    print("=" * 70)
    
    # Check if database exists
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        print("Please ensure cutter.db exists in the current directory.")
        sys.exit(1)
    
    print(f"[SUCCESS] Database found: {DB_PATH}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Enable WAL mode for concurrency (v2.1 requirement)
        cursor.execute("PRAGMA journal_mode=WAL;")
        print("[SUCCESS] WAL mode enabled for database concurrency")
        
        print("\n" + "=" * 70)
        print("STEP 1: Seed Pricing Tags (The Universal 9)")
        print("=" * 70)
        
        # Create pricing_tags table if it doesn't exist
        if not check_table_exists(cursor, 'pricing_tags'):
            print("[INFO] Creating pricing_tags table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pricing_tags (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    default_markup REAL,
                    description TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            conn.commit()
            print("[SUCCESS] Created pricing_tags table")
        else:
            print("[INFO] pricing_tags table already exists")
        
        # Check if table is empty
        if is_table_empty(cursor, 'pricing_tags'):
            print("[INFO] pricing_tags table is empty. Seeding Universal 9 tags...")
            
            # The Universal 9 Tags (Pricing)
            universal_9_tags = [
                ("Rush Job", 20.0, "Expedited delivery timeline", 1),
                ("Expedite", 15.0, "Faster than standard but not full rush", 1),
                ("Risk: Scrap High", 25.0, "High risk of scrap due to tight tolerances or difficult material", 1),
                ("Friends / Family", -10.0, "Discount for personal relationships", 1),
                ("Tight Tol", 30.0, "Tight tolerances requiring precision machining", 1),
                ("Complex Fixture", 20.0, "Requires custom fixturing or complex setup", 1),
                ("Heavy Deburr", 15.0, "Extensive deburring required", 1),
                ("Proto", 10.0, "Prototype run with potential for future orders", 1),
                ("Cust. Material", 5.0, "Customer-supplied material", 1)
            ]
            
            for name, markup, desc, active in universal_9_tags:
                cursor.execute("""
                    INSERT INTO pricing_tags (name, default_markup, description, is_active)
                    VALUES (?, ?, ?, ?)
                """, (name, markup, desc, active))
                print(f"  [ADDED] {name} ({markup:+.1f}%)")
            
            conn.commit()
            print(f"[SUCCESS] Seeded 9 pricing tags")
        else:
            cursor.execute("SELECT COUNT(*) FROM pricing_tags WHERE is_active = 1")
            active_count = cursor.fetchone()[0]
            print(f"[INFO] pricing_tags table already has data ({active_count} active tags). Skipping seed.")
        
        print("\n" + "=" * 70)
        print("STEP 2: Add O-Score Variance Tracking Columns")
        print("=" * 70)
        
        # Check if O-Score columns exist
        if check_column_exists(cursor, 'quote_history', 'system_price_anchor'):
            print("[INFO] O-Score columns already exist. Skipping...")
        else:
            print("[INFO] Adding O-Score columns to quote_history...")
            
            # Add variance tracking columns
            columns_to_add = [
                ('user_id', 'INTEGER', 'Track WHO created the quote'),
                ('system_price_anchor', 'REAL', 'The raw physics output (The Truth)'),
                ('final_quoted_price', 'REAL', 'What Bob actually charged'),
                ('variance_json', 'TEXT', 'JSON object with variance attribution'),
                ('is_guild_synced', 'INTEGER DEFAULT 0', 'Customer portal sync flag')
            ]
            
            for column_name, column_type, description in columns_to_add:
                try:
                    print(f"  [ADDING] {column_name} ({description})")
                    cursor.execute(f"ALTER TABLE ops__quote_history ADD COLUMN {column_name} {column_type}")
                    print(f"  [SUCCESS] Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"  [SKIP] Column {column_name} already exists")
                    else:
                        raise
            
            conn.commit()
            print("[SUCCESS] Added O-Score columns")
        
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)
        
        # Verify pricing tags
        cursor.execute("SELECT COUNT(*) FROM pricing_tags WHERE is_active = 1")
        active_tags = cursor.fetchone()[0]
        print(f"[VERIFIED] pricing_tags table has {active_tags} active tags")
        
        # Verify O-Score columns
        oscore_columns = ['user_id', 'system_price_anchor', 'final_quoted_price', 'variance_json', 'is_guild_synced']
        all_exist = True
        for col in oscore_columns:
            if check_column_exists(cursor, 'quote_history', col):
                print(f"[VERIFIED] ✓ {col} exists in quote_history")
            else:
                print(f"[ERROR] ✗ {col} NOT FOUND in quote_history")
                all_exist = False
        
        conn.close()
        
        if not all_exist:
            print("\n[ERROR] Some columns were not created. Please check errors above.")
            sys.exit(1)
        
        print("\n" + "=" * 70)
        print("[SUCCESS] Phase 4 Database Preparation Complete")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"  ✓ Pricing Tags: {active_tags} active tags ready")
        print("  ✓ O-Score Columns: All 5 variance tracking columns added")
        print("  ✓ WAL Mode: Enabled for mobile node concurrency")
        print("\n🚀 Next Steps:")
        print("  1. Restart Flask server (if running)")
        print("  2. Test Glass Box variance feature")
        print("  3. Verify pricing tags appear in UI")
        print("  4. Create a test quote with variance attribution")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

