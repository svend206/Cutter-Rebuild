"""
Migration Script: Add O-Score Variance Tracking Columns
Date: December 28, 2025
Purpose: Add columns to quote_history for Glass Box variance tracking and O-Score calculation.

This migration adds:
- user_id: Track WHO created the quote
- system_price_anchor: The raw physics output (The Truth)
- final_quoted_price: What Bob actually charged
- variance_json: JSON object with variance attribution
- is_guild_synced: Customer portal sync flag
"""

import sqlite3
import sys
from pathlib import Path

# Database path
DB_PATH = Path("cutter.db")

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    return column_name in column_names

def main():
    print("=" * 60)
    print("MIGRATION: Add O-Score Variance Tracking Columns")
    print("=" * 60)
    
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
        
        # Check if migration is needed
        if check_column_exists(cursor, 'quote_history', 'system_price_anchor'):
            print("[INFO] Migration already applied. Columns already exist.")
            print("[SUCCESS] Migration Successful (No Changes Needed)")
            conn.close()
            return
        
        print("[INFO] Applying migration...")
        
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
                print(f"[ADDING] {column_name} ({description})")
                cursor.execute(f"ALTER TABLE ops__quote_history ADD COLUMN {column_name} {column_type}")
                print(f"[SUCCESS] Added column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"[SKIP] Column {column_name} already exists")
                else:
                    raise
        
        # Commit changes
        conn.commit()
        print("[SUCCESS] All columns added successfully")
        
        # Verify columns were added
        print("\n[VERIFICATION] Checking new columns...")
        cursor.execute("PRAGMA table_info(quote_history)")
        columns = cursor.fetchall()
        
        new_columns = ['user_id', 'system_price_anchor', 'final_quoted_price', 'variance_json', 'is_guild_synced']
        for new_col in new_columns:
            if check_column_exists(cursor, 'quote_history', new_col):
                print(f"[VERIFIED] ✓ {new_col} exists")
            else:
                print(f"[ERROR] ✗ {new_col} NOT FOUND")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Migration Successful")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Restart Flask server (if running)")
        print("2. Test quote creation to verify variance tracking")
        print("3. Check database with: sqlite3 cutter.db \".schema quote_history\"")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

