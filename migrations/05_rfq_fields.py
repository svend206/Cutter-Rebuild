"""
Migration 05: Add RFQ-First Fields to quotes table
Date: 2026-01-02
Purpose: Support full RFQ data capture before anchor calculation
         Enables "False Anchor" prevention and pattern matching

Fields Added:
- lead_time_date: Target delivery date from RFQ
- lead_time_days: Calculated days from quote date to target
- target_price_per_unit: Customer's budget hint (optional)
- price_breaks_json: Array of quantities for price breaks
- outside_processing_json: Required outside ops (Anodize, Heat Treat, etc.)
- quality_requirements_json: Quality/inspection requirements (CMM, AS9102, etc.)
- part_marking_json: Part marking requirements (Laser Etch, etc.)
"""
import sqlite3
import os
from datetime import datetime

def migrate():
    """Add RFQ-First fields to quotes table."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'cutter.db')
    
    if not os.path.exists(db_path):
        print(f"[MIGRATION 05] Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Enable WAL mode
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Check which columns already exist
        cursor.execute("PRAGMA table_info(quotes);")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        new_columns = {
            'lead_time_date': 'TEXT',  # ISO format: YYYY-MM-DD
            'lead_time_days': 'INTEGER',  # Calculated from quote date to target
            'target_price_per_unit': 'REAL',  # Customer budget hint (optional)
            'price_breaks_json': 'TEXT',  # JSON array: [1, 5, 25, 100]
            'outside_processing_json': 'TEXT',  # JSON array: ["Anodize (Type II)", "Heat Treat"]
            'quality_requirements_json': 'TEXT',  # JSON: {"cmm": true, "as9102": false, "notes": "..."}
            'part_marking_json': 'TEXT'  # JSON: {"type": "Laser Etch", "content": "PART-12345"}
        }
        
        added_count = 0
        for col_name, col_type in new_columns.items():
            if col_name in existing_columns:
                print(f"[MIGRATION 05] Column '{col_name}' already exists. Skipping.")
            else:
                print(f"[MIGRATION 05] Adding column '{col_name}' ({col_type})...")
                cursor.execute(f"ALTER TABLE ops__quotes ADD COLUMN {col_name} {col_type};")
                added_count += 1
        
        if added_count > 0:
            conn.commit()
            print(f"[MIGRATION 05] SUCCESS - Added {added_count} columns")
        else:
            print("[MIGRATION 05] All columns already exist. No changes made.")
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(quotes);")
        all_columns = [col[1] for col in cursor.fetchall()]
        print(f"[MIGRATION 05] Final column count: {len(all_columns)}")
        
        # Show new columns
        new_cols_added = [col for col in new_columns.keys() if col in all_columns]
        if new_cols_added:
            print(f"[MIGRATION 05] New RFQ fields available: {', '.join(new_cols_added)}")
        
    except Exception as e:
        print(f"[MIGRATION 05] ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()

