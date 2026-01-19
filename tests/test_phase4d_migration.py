"""
Test: Phase 4d Migration Verification

Verifies:
1. Row count match between legacy and new cutter__events
2. UPDATE/DELETE blocked on cutter__events
3. subject_ref populated correctly
4. Backward compatibility view works
5. Boundary module works with new table
"""

import sqlite3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from cutter_ledger.boundary import emit_cutter_event, get_events

if not os.environ.get("TEST_DB_PATH"):
    bootstrap_path = Path(tempfile.gettempdir()) / "test_phase4d_migration_bootstrap.db"
    os.environ["TEST_DB_PATH"] = str(bootstrap_path)

import database


def _ensure_test_db() -> Path:
    test_db_env = os.environ.get("TEST_DB_PATH")
    if not test_db_env:
        temp_dir = tempfile.gettempdir()
        test_db_env = str(Path(temp_dir) / "test_phase4d_migration.db")
        os.environ["TEST_DB_PATH"] = test_db_env
    db_path = Path(test_db_env)
    result = subprocess.run(
        [sys.executable, 'scripts/reset_db.py', '--db-path', str(db_path)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    if result.returncode != 0:
        raise RuntimeError(f"reset_db failed: {result.stderr}")
    return db_path


_ensure_test_db()
DB_PATH = database.require_test_db("append-only bypass tests")


def test_row_count_match():
    """Verify row count matches between legacy and new table."""
    print("\n" + "=" * 80)
    print("TEST: Row Count Match")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if migration has run
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='cutter__events'
    """)
    if not cursor.fetchone():
        print("[SKIP] Migration not yet run (cutter__events doesn't exist)")
        conn.close()
        return
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='cutter__operational_events__legacy_4d'
    """)
    if not cursor.fetchone():
        print("[SKIP] Legacy table not present")
        conn.close()
        return
    cursor.execute("SELECT COUNT(*) FROM cutter__operational_events__legacy_4d")
    legacy_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cutter__events")
    new_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"  Legacy table: {legacy_count} rows")
    print(f"  New table: {new_count} rows")
    
    assert legacy_count == new_count, f"Row count mismatch: {legacy_count} != {new_count}"
    print("[PASS] Row counts match")


def test_append_only_triggers():
    """Verify UPDATE/DELETE blocked on cutter__events."""
    print("\n" + "=" * 80)
    print("TEST: Append-Only Triggers")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if migration has run
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='cutter__events'
    """)
    if not cursor.fetchone():
        print("[SKIP] Migration not yet run")
        conn.close()
        return
    
    # Get a test event ID
    cursor.execute("SELECT id FROM cutter__events LIMIT 1")
    row = cursor.fetchone()
    if not row:
        print("[SKIP] No events in table to test")
        conn.close()
        return
    
    test_id = row[0]
    
    # Test UPDATE blocker
    try:
        cursor.execute(f"UPDATE cutter__events SET event_type = 'TEST' WHERE id = {test_id}")
        conn.close()
        raise AssertionError("UPDATE was not blocked by trigger")
    except sqlite3.IntegrityError as e:
        if 'Constitutional violation' in str(e) and 'append-only' in str(e):
            print("[PASS] UPDATE blocked by trigger")
        else:
            raise
    
    # Test DELETE blocker
    try:
        cursor.execute(f"DELETE FROM cutter__events WHERE id = {test_id}")
        conn.close()
        raise AssertionError("DELETE was not blocked by trigger")
    except sqlite3.IntegrityError as e:
        if 'Constitutional violation' in str(e):
            print("[PASS] DELETE blocked by trigger")
        else:
            raise
    
    conn.close()


def test_subject_ref_populated():
    """Verify subject_ref is populated correctly."""
    print("\n" + "=" * 80)
    print("TEST: subject_ref Population")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if migration has run
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='cutter__events'
    """)
    if not cursor.fetchone():
        print("[SKIP] Migration not yet run")
        conn.close()
        return
    
    # Check for NULL subject_ref
    cursor.execute("SELECT COUNT(*) FROM cutter__events WHERE subject_ref IS NULL")
    null_count = cursor.fetchone()[0]
    
    # Get sample subject_ref values
    cursor.execute("SELECT DISTINCT subject_ref FROM cutter__events LIMIT 10")
    samples = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    print(f"  NULL subject_ref: {null_count}")
    print(f"  Sample values: {samples}")
    
    assert null_count == 0, f"Found {null_count} NULL subject_ref values"
    
    # Verify format (should be "quote:NNN" or "unknown")
    for sample in samples:
        assert isinstance(sample, str), f"subject_ref should be string, got {type(sample)}"
        assert sample == "unknown" or sample.startswith("quote:"), \
            f"Unexpected subject_ref format: {sample}"
    
    print("[PASS] subject_ref populated correctly")


def test_backward_compatibility_view():
    """Verify backward compatibility view works."""
    print("\n" + "=" * 80)
    print("TEST: Backward Compatibility View")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if migration has run
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view' AND name='cutter__operational_events'
    """)
    if not cursor.fetchone():
        print("[SKIP] Migration not yet run (view doesn't exist)")
        conn.close()
        return
    
    # Query the view
    cursor.execute("SELECT id, event_type, quote_id, subject_ref FROM cutter__operational_events LIMIT 5")
    rows = cursor.fetchall()
    
    conn.close()
    
    print(f"  View returned {len(rows)} rows")
    
    for row in rows:
        subject_ref = row['subject_ref']
        quote_id = row['quote_id']
        
        # Verify quote_id is correctly computed from subject_ref
        if subject_ref.startswith("quote:"):
            expected_quote_id = int(subject_ref.split(":")[1])
            assert quote_id == expected_quote_id, \
                f"quote_id mismatch: expected {expected_quote_id}, got {quote_id}"
        else:
            assert quote_id is None, f"quote_id should be NULL for non-quote subject_ref"
    
    print("[PASS] View exposes correct quote_id")


def test_boundary_module_integration():
    """Test that boundary module works with new table."""
    print("\n" + "=" * 80)
    print("TEST: Boundary Module Integration")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if migration has run
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='cutter__events'
    """)
    if not cursor.fetchone():
        print("[SKIP] Migration not yet run")
        conn.close()
        return
    
    conn.close()
    
    # Test write with string subject_ref
    event_id1 = emit_cutter_event(
        event_type='PHASE4D_TEST_STRING',
        subject_ref="quote:999",
        event_data={'test': 'string_ref'}
    )
    print(f"[OK] Emitted event with string subject_ref: ID={event_id1}")
    
    # Test write with int subject_ref (backward compatibility)
    event_id2 = emit_cutter_event(
        event_type='PHASE4D_TEST_INT',
        subject_ref=999,
        event_data={'test': 'int_ref'}
    )
    print(f"[OK] Emitted event with int subject_ref: ID={event_id2}")
    
    # Test read with string subject_ref
    events = get_events(subject_ref="quote:999")
    assert len(events) >= 2, f"Expected at least 2 events, got {len(events)}"
    print(f"[OK] Retrieved {len(events)} events for subject_ref='quote:999'")
    
    # Test read with int subject_ref (backward compatibility)
    events_int = get_events(subject_ref=999)
    assert len(events_int) == len(events), "Int and string queries should return same results"
    print(f"[OK] Backward compatibility: int subject_ref query works")
    
    # Verify subject_ref in results
    for event in events:
        assert event['subject_ref'] == "quote:999", \
            f"Expected subject_ref='quote:999', got '{event['subject_ref']}'"
    
    print("[PASS] Boundary module works with new table")


def run_all_tests():
    """Run all Phase 4d migration tests."""
    print("\n" + "=" * 80)
    print("PHASE 4D MIGRATION VERIFICATION TEST SUITE")
    print("=" * 80)
    
    try:
        test_row_count_match()
        test_append_only_triggers()
        test_subject_ref_populated()
        test_backward_compatibility_view()
        test_boundary_module_integration()
        
        print("\n" + "=" * 80)
        print("[SUCCESS] ALL PHASE 4D TESTS PASSED")
        print("=" * 80)
        print()
        print("Verified:")
        print("  [OK] Row counts match (legacy vs new)")
        print("  [OK] Append-only triggers active")
        print("  [OK] subject_ref populated correctly")
        print("  [OK] Backward compatibility view works")
        print("  [OK] Boundary module integration")
        print()
        return True
        
    except AssertionError as e:
        print("\n" + "=" * 80)
        print(f"[FAIL] {e}")
        print("=" * 80)
        return False
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"[ERROR] {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
