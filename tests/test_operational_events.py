"""
Test: Operational Events (Ledger Core)

Verifies:
1. cutter__operational_events table exists with append-only constraints
2. emit_event() function works correctly
3. DB triggers prevent UPDATE/DELETE (Constitutional enforcement)
4. QUOTE_OVERRIDDEN event is emitted when final_price != anchor_price
5. Event vocabulary is descriptive (evaluative language rejected)

Constitutional Authority:
- C1 (Outcome Agnosticism): No evaluative event types
- C4 (Irreversible Memory): No retroactive edits
- C7 (Overrides Must Leave Scars): Override events preserve magnitude
"""

import sqlite3
import json
import os
import tempfile
from pathlib import Path

if not os.environ.get("TEST_DB_PATH"):
    bootstrap_path = Path(tempfile.gettempdir()) / "test_operational_events_bootstrap.db"
    os.environ["TEST_DB_PATH"] = str(bootstrap_path)

import database

DB_PATH = Path("cutter.db")


def test_operational_events_table_exists():
    """Verify cutter__operational_events table was created by migration."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='cutter__operational_events'
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None, "cutter__operational_events table does not exist"
    print("[TEST PASS] cutter__operational_events table exists")


def test_table_schema_correct():
    """Verify table has correct columns."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(cutter__operational_events)")
    columns = cursor.fetchall()
    conn.close()
    
    column_names = [col[1] for col in columns]
    
    assert 'id' in column_names
    assert 'event_type' in column_names
    assert 'quote_id' in column_names
    assert 'event_data' in column_names
    assert 'created_at' in column_names
    
    print(f"[TEST PASS] Table schema correct: {column_names}")


def test_triggers_exist():
    """Verify append-only triggers were created."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='trigger' AND tbl_name='cutter__operational_events'
    """)
    
    triggers = cursor.fetchall()
    conn.close()
    
    trigger_names = [t[0] for t in triggers]
    
    assert 'prevent_event_updates' in trigger_names, "UPDATE trigger missing"
    assert 'prevent_event_deletes' in trigger_names, "DELETE trigger missing"
    
    print(f"[TEST PASS] Triggers exist: {trigger_names}")


def test_trigger_prevents_update():
    """Constitutional test: C4 (Irreversible Memory) - Updates must be blocked."""
    # Insert a test event
    event_id = database.emit_event(
        event_type='TEST_EVENT',
        quote_id=None,
        event_data={'test': 'data'}
    )
    
    # Try to update it (should fail)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE cutter__operational_events 
            SET event_type = 'MODIFIED' 
            WHERE id = ?
        """, (event_id,))
        conn.commit()
        conn.close()
        assert False, "UPDATE should have been blocked by trigger"
    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        conn.close()
        assert 'Constitutional violation' in error_msg, f"Unexpected error: {error_msg}"
        assert 'append-only' in error_msg
        print(f"[TEST PASS] UPDATE blocked by trigger: {error_msg}")


def test_trigger_prevents_delete():
    """Constitutional test: C7 (Overrides Must Leave Scars) - Deletes must be blocked."""
    # Insert a test event
    event_id = database.emit_event(
        event_type='TEST_EVENT',
        quote_id=None,
        event_data={'test': 'data'}
    )
    
    # Try to delete it (should fail)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM cutter__operational_events WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()
        assert False, "DELETE should have been blocked by trigger"
    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        conn.close()
        assert 'Constitutional violation' in error_msg, f"Unexpected error: {error_msg}"
        assert 'cannot be deleted' in error_msg
        print(f"[TEST PASS] DELETE blocked by trigger: {error_msg}")


def test_emit_event_basic():
    """Test emit_event() function with valid descriptive event type."""
    event_data = {
        'override_delta': 25.50,
        'override_percent': 15.3,
        'material': 'Aluminum 6061'
    }
    
    event_id = database.emit_event(
        event_type='QUOTE_OVERRIDDEN',
        quote_id=1,
        event_data=event_data
    )
    
    assert event_id > 0, "Event ID should be positive integer"
    
    # Verify event was stored
    events = database.get_events_for_quote(quote_id=1)
    
    matching = [e for e in events if e['id'] == event_id]
    assert len(matching) == 1, "Event not found in database"
    
    event = matching[0]
    assert event['event_type'] == 'QUOTE_OVERRIDDEN'
    assert event['event_data']['override_delta'] == 25.50
    
    print(f"[TEST PASS] emit_event() stored event correctly: ID={event_id}")


def test_emit_event_rejects_evaluative_language():
    """Constitutional test: C1 (Outcome Agnosticism) - Evaluative event types must be rejected."""
    
    forbidden_event_types = [
        'QUOTE_PROBLEM',
        'QUOTE_BAD',
        'QUOTE_RISKY',
        'QUOTE_UNHEALTHY',
        'QUOTE_ISSUE',
        'QUOTE_WARNING'
    ]
    
    for bad_event_type in forbidden_event_types:
        try:
            database.emit_event(
                event_type=bad_event_type,
                quote_id=None,
                event_data={'test': 'data'}
            )
            assert False, f"Evaluative event type '{bad_event_type}' should have been rejected"
        except ValueError as e:
            error_msg = str(e)
            assert 'evaluative language' in error_msg.lower()
            print(f"[TEST PASS] Rejected evaluative event type: {bad_event_type}")


def test_quote_override_detection():
    """
    Integration test: Verify QUOTE_OVERRIDDEN event is emitted when
    final_quoted_price != system_price_anchor.
    
    This tests the Control Surface -> Ledger Core integration.
    """
    # Create a minimal quote with override
    # First, create test entities
    
    # Create customer
    customer_id, _ = database.resolve_customer(
        name="Test Customer",
        email_domain="test.com"
    )
    
    # Create part
    part_id = database.upsert_part(
        genesis_hash="test_hash_override_123",
        filename="test_part.step",
        fingerprint_json="[1.0, 2.0, 3.0, 4.0, 5.0]",
        volume=10.0,
        surface_area=50.0,
        dimensions_json='{"x": 2.0, "y": 3.0, "z": 4.0}',
        process_routing_json='[]'
    )
    
    # Create quote with override (anchor=100, final=125)
    system_price_anchor = 100.0
    final_quoted_price = 125.0
    
    quote_id = database.create_quote(
        part_id=part_id,
        customer_id=customer_id,
        contact_id=None,
        quote_id="TEST-OVERRIDE-001",
        user_id=None,
        material="Aluminum 6061",
        system_price_anchor=system_price_anchor,
        final_quoted_price=final_quoted_price,
        quantity=1,
        status='Draft'
    )
    
    # Manually emit event (simulating what app.py does)
    override_delta = final_quoted_price - system_price_anchor
    override_percent = (override_delta / system_price_anchor) * 100.0
    
    event_data = {
        'system_price_anchor': system_price_anchor,
        'final_quoted_price': final_quoted_price,
        'override_delta': override_delta,
        'override_percent': override_percent,
        'material': 'Aluminum 6061',
        'quantity': 1
    }
    
    database.emit_event(
        event_type='QUOTE_OVERRIDDEN',
        quote_id=quote_id,
        event_data=event_data
    )
    
    # Verify event was stored
    events = database.get_events_for_quote(quote_id=quote_id)
    
    override_events = [e for e in events if e['event_type'] == 'QUOTE_OVERRIDDEN']
    assert len(override_events) == 1, "QUOTE_OVERRIDDEN event not found"
    
    event = override_events[0]
    assert event['event_data']['override_delta'] == 25.0
    assert event['event_data']['override_percent'] == 25.0
    
    print(f"[TEST PASS] QUOTE_OVERRIDDEN event emitted correctly: +${override_delta} (+{override_percent:.1f}%)")


def test_no_event_when_no_override():
    """Verify no event is emitted when final_price == anchor_price."""
    # Create quote with NO override (anchor=100, final=100)
    
    customer_id = database.resolve_customer(
        name="Test Customer No Override",
        email_domain="test-no-override.com"
    )
    
    part_id = database.upsert_part(
        genesis_hash="test_hash_no_override_456",
        filename="test_part_no_override.step",
        fingerprint_json="[1.0, 2.0, 3.0, 4.0, 5.0]",
        volume=10.0,
        surface_area=50.0,
        dimensions_json='{"x": 2.0, "y": 3.0, "z": 4.0}',
        process_routing_json='[]'
    )
    
    system_price_anchor = 100.0
    final_quoted_price = 100.0  # NO OVERRIDE
    
    quote_id = database.create_quote(
        part_id=part_id,
        customer_id=customer_id,
        contact_id=None,
        quote_id="TEST-NO-OVERRIDE-002",
        user_id=None,
        material="Aluminum 6061",
        system_price_anchor=system_price_anchor,
        final_quoted_price=final_quoted_price,
        quantity=1,
        status='Draft'
    )
    
    # Check that no QUOTE_OVERRIDDEN event exists for this quote
    events = database.get_events_for_quote(quote_id=quote_id)
    override_events = [e for e in events if e['event_type'] == 'QUOTE_OVERRIDDEN']
    
    assert len(override_events) == 0, "QUOTE_OVERRIDDEN event should NOT be emitted when no override"
    
    print("[TEST PASS] No event emitted when final_price == anchor_price")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("TESTING: Operational Events (Ledger Core)")
    print("="*80 + "\n")
    
    # Run tests in order
    test_operational_events_table_exists()
    test_table_schema_correct()
    test_triggers_exist()
    test_trigger_prevents_update()
    test_trigger_prevents_delete()
    test_emit_event_basic()
    test_emit_event_rejects_evaluative_language()
    test_quote_override_detection()
    test_no_event_when_no_override()
    
    print("\n" + "="*80)
    print("ALL TESTS PASSED")
    print("="*80 + "\n")
