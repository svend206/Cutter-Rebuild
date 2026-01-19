#!/usr/bin/env python3
"""
State Ledger Schema Inspector

Prints complete schema information for State Ledger tables and views.
"""

import sys
import os
import json
import sqlite3
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import database


def main():
    """Inspect State Ledger schema."""
    
    # Get database path
    test_db_path = os.environ.get('TEST_DB_PATH')
    if test_db_path:
        db_path = Path(test_db_path)
    else:
        db_path = Path(database.DB_PATH)
    
    result = {
        "db_path": str(db_path),
        "db_exists": db_path.exists(),
    }
    
    if not db_path.exists():
        result["error"] = "Database file does not exist"
        print(json.dumps(result, indent=2))
        return 1
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get table schemas
    tables = ['state__declarations', 'state__entities', 'state__recognition_owners']
    
    result["tables"] = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        result["tables"][table] = [
            {
                "cid": col[0],
                "name": col[1],
                "type": col[2],
                "notnull": bool(col[3]),
                "default_value": col[4],
                "pk": bool(col[5])
            }
            for col in columns
        ]
    
    # Get views
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view' AND name LIKE 'view_ds%'
        ORDER BY name
    """)
    result["views"] = [row[0] for row in cursor.fetchall()]
    
    # Get triggers on state__declarations
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='trigger' AND tbl_name='state__declarations'
        ORDER BY name
    """)
    result["triggers"] = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
