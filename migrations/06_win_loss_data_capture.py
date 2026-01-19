"""
Migration 06: Win/Loss Data Capture (The "Deal Closer")
Date: 2026-01-04
Purpose: Add columns to capture win/loss reasons and closure timestamps
         Enables post-mortem analysis and pattern recognition for sales intelligence

Fields Added:
- loss_reason: TEXT - Reason(s) for losing the quote (Price, Lead Time, Ghosted, Capability, Other)
- win_notes: TEXT - Optional notes about why we won (e.g., "Final agreed price", "Relationship", etc.)
- closed_at: DATETIME - Timestamp when quote was marked Won/Lost (NULL for Draft/Sent)

Rationale:
- loss_reason was referenced in database.py but column didn't exist
- Closing the feedback loop: Know WHY quotes are won or lost
- Pattern recognition: "We always lose aerospace quotes on lead time"
"""
import sqlite3
import os
from datetime import datetime

def migrate():
    """Add Win/Loss data capture fields to quotes table."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'cutter.db')
    
    if not os.path.exists(db_path):
        print(f"[MIGRATION 06] Database not found at {db_path}")
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
            'loss_reason': 'TEXT',  # JSON array or single string: ["Price", "Lead Time"]
            'win_notes': 'TEXT',  # Free-form notes about why we won
            'closed_at': 'DATETIME'  # Timestamp when marked Won/Lost
        }
        
        added_count = 0
        for col_name, col_type in new_columns.items():
            if col_name in existing_columns:
                print(f"[MIGRATION 06] Column '{col_name}' already exists. Skipping.")
            else:
                print(f"[MIGRATION 06] Adding column '{col_name}' ({col_type})...")
                cursor.execute(f"ALTER TABLE ops__quotes ADD COLUMN {col_name} {col_type};")
                added_count += 1
        
        if added_count > 0:
            conn.commit()
            print(f"[MIGRATION 06] SUCCESS - Added {added_count} columns")
        else:
            print("[MIGRATION 06] All columns already exist. No changes made.")
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(quotes);")
        all_columns = [col[1] for col in cursor.fetchall()]
        print(f"[MIGRATION 06] Final column count: {len(all_columns)}")
        
        # Show new columns
        new_cols_added = [col for col in new_columns.keys() if col in all_columns]
        if new_cols_added:
            print(f"[MIGRATION 06] New Win/Loss fields available: {', '.join(new_cols_added)}")
        
        print("\n[NEXT STEPS]")
        print("  1. Update database.update_quote_status() to set closed_at")
        print("  2. Create new endpoint POST /api/quote/<id>/update_status")
        print("  3. Make sidebar status badges clickable")
        print("  4. Create status update modal in index.html")
        print("  5. Restart Flask server")
        
    except Exception as e:
        print(f"[MIGRATION 06] ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()

