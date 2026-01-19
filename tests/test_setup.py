"""
Test Database Setup - Hermetic Test Environment
Creates an isolated test database for each test run.

This ensures tests are hermetic and don't pollute production data.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import database


def setup_test_database():
    """
    Create a fresh test database in a temporary location.
    Returns the path to the test database.
    """
    # Create temp directory for test database
    temp_dir = tempfile.gettempdir()
    test_db_path = Path(temp_dir) / "cutter_test.db"
    
    # Remove old test DB if it exists
    if test_db_path.exists():
        test_db_path.unlink()
    
    print(f"[TEST SETUP] Creating isolated test database: {test_db_path}")
    
    # Set environment variable so database.py uses test DB
    os.environ["TEST_DB_PATH"] = str(test_db_path)
    
    # Reload database module to pick up new DB_PATH
    import importlib
    importlib.reload(database)
    
    # Initialize database schema
    print("[TEST SETUP] Initializing database schema...")
    database.initialize_database()
    
    print(f"[TEST SETUP] Test database ready at: {test_db_path}")
    print(f"[TEST SETUP] Size: {test_db_path.stat().st_size / 1024:.1f} KB")
    
    return test_db_path


def cleanup_test_database(test_db_path):
    """
    Clean up test database after tests complete.
    """
    if test_db_path and Path(test_db_path).exists():
        print(f"\n[TEST CLEANUP] Removing test database: {test_db_path}")
        Path(test_db_path).unlink()
        print("[TEST CLEANUP] Test database removed")


if __name__ == "__main__":
    import sys
    
    # Check if this is a verification run or setup-only run
    if "--verify-only" in sys.argv:
        # Quick test: create, verify, and cleanup
        test_db = setup_test_database()
        
        # Verify we can connect and query
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"\n[VERIFICATION] Found {len(tables)} tables in test database:")
        for table in tables[:5]:
            print(f"  - {table[0]}")
        if len(tables) > 5:
            print(f"  ... and {len(tables) - 5} more")
        
        print("\n[SUCCESS] Test database setup verified!")
        
        # Cleanup
        cleanup_test_database(test_db)
    else:
        # Setup only - leave DB for test suite to use
        test_db = setup_test_database()
        print("\n[SUCCESS] Test database ready for test suite!")
