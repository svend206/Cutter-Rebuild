"""
Test: Cutter Ledger Boundary Enforcement

Verifies:
1. Only cutter_ledger/boundary.py contains direct INSERTs to cutter__operational_events
2. emit_cutter_event() correctly validates and writes
3. ingested_by field is auto-populated
4. All other modules use the boundary (no backdoor writes)

Constitutional Authority:
- Boundary consolidation ensures single write path
- Provenance tracking via ingested_by
- Constitutional validation enforced at entry point
"""

import sqlite3
import json
import re
from pathlib import Path
import sys


DB_PATH = Path("cutter.db")


def test_only_boundary_writes_to_ledger():
    """
    Verify that direct INSERTs to cutter__operational_events only occur in boundary.py.
    
    This test scans all Python files (excluding Ops Layer, tests, and migrations)
    and asserts that no module directly writes to the Cutter Ledger except boundary.py.
    """
    print("\n" + "=" * 80)
    print("TEST: Boundary Enforcement - Single Write Path")
    print("=" * 80)
    
    root_dir = Path('.')
    violations = []
    
    # Pattern to detect direct INSERTs to cutter__operational_events
    insert_pattern = re.compile(r'INSERT\s+INTO\s+cutter__operational_events', re.IGNORECASE)
    
    for py_file in root_dir.rglob('*.py'):
        # Skip excluded directories
        if 'Ops Layer' in str(py_file) or '_archive' in str(py_file):
            continue
        
        # Skip test files and boundary.py itself
        if py_file.name.startswith('test_') or py_file.name == 'boundary.py':
            continue
        
        # Skip migration scripts (they create the table)
        if 'migrations' in str(py_file):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            if insert_pattern.search(content):
                violations.append(str(py_file))
        except Exception:
            pass
    
    if violations:
        print(f"[FAIL] Found {len(violations)} backdoor writes to cutter__operational_events:")
        for v in violations:
            print(f"  - {v}")
        raise AssertionError(
            f"Constitutional violation: {len(violations)} file(s) bypass the Cutter Ledger boundary. "
            f"All writes must go through cutter_ledger.boundary.emit_cutter_event()"
        )
    
    print("[PASS] No backdoor writes detected")
    print("  Only cutter_ledger/boundary.py contains direct INSERTs")


def test_emit_cutter_event_validates():
    """Test that emit_cutter_event() enforces constitutional validation."""
    print("\n" + "=" * 80)
    print("TEST: Constitutional Validation at Boundary")
    print("=" * 80)
    
    from cutter_ledger.boundary import emit_cutter_event
    
    # Test valid event
    try:
        event_id = emit_cutter_event(
            event_type='TEST_BOUNDARY_EVENT',
            subject_ref=None,
            event_data={'test': 'valid'}
        )
        print(f"[PASS] Valid event accepted: ID={event_id}")
    except Exception as e:
        raise AssertionError(f"Valid event rejected: {e}")
    
    # Test evaluative language rejection
    forbidden_types = ['ENTITY_PROBLEM', 'BAD_PRICE', 'GOOD_OUTCOME', 'RISKY_WORKFLOW']
    for bad_type in forbidden_types:
        try:
            emit_cutter_event(
                event_type=bad_type,
                subject_ref=None,
                event_data={}
            )
            raise AssertionError(f"Evaluative event type '{bad_type}' was accepted (should be rejected)")
        except ValueError as e:
            if 'evaluative language' in str(e):
                print(f"[PASS] Rejected evaluative type: {bad_type}")
            else:
                raise


def test_deterministic_provenance():
    """Test that deterministic provenance (service_id + version) is recorded."""
    print("\n" + "=" * 80)
    print("TEST: Deterministic Provenance")
    print("=" * 80)
    
    from cutter_ledger.boundary import emit_cutter_event
    
    # Emit event with deterministic provenance
    event_id = emit_cutter_event(
        event_type='TEST_PROVENANCE',
        subject_ref=None,
        event_data={'test': 'provenance'}
    )
    
    # Verify deterministic provenance was recorded
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ingested_by_service, ingested_by_version, event_data FROM cutter__operational_events WHERE id = ?",
        (event_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None, "Event not found in database"
    service_id, version, event_data_json = row
    
    assert service_id is not None, "ingested_by_service was not populated"
    assert version is not None, "ingested_by_version was not populated"
    assert service_id == "cutter_ops_v1", f"Expected 'cutter_ops_v1', got: {service_id}"
    
    # Verify debug callsite is in event_data (best-effort)
    event_data = json.loads(event_data_json) if event_data_json else {}
    assert 'debug' in event_data, "Debug metadata missing"
    assert 'callsite' in event_data['debug'], "Callsite missing from debug metadata"
    
    print(f"[PASS] Deterministic provenance recorded:")
    print(f"  service_id: {service_id}")
    print(f"  version: {version}")
    print(f"  debug.callsite: {event_data['debug']['callsite']}")


def test_explicit_provenance_override():
    """Test that explicit service_id and version can be provided."""
    print("\n" + "=" * 80)
    print("TEST: Explicit Provenance Override")
    print("=" * 80)
    
    from cutter_ledger.boundary import emit_cutter_event
    
    # Emit event with explicit provenance
    explicit_service = "test_system_v2"
    explicit_version = "abc123"
    event_id = emit_cutter_event(
        event_type='TEST_EXPLICIT_PROVENANCE',
        subject_ref=None,
        event_data={'test': 'explicit'},
        service_id=explicit_service,
        version=explicit_version
    )
    
    # Verify explicit values were preserved
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ingested_by_service, ingested_by_version FROM cutter__operational_events WHERE id = ?",
        (event_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None, "Event not found in database"
    service_id, version = row
    
    assert service_id == explicit_service, f"Expected '{explicit_service}', got '{service_id}'"
    assert version == explicit_version, f"Expected '{explicit_version}', got '{version}'"
    
    print(f"[PASS] Explicit provenance preserved:")
    print(f"  service_id: {service_id}")
    print(f"  version: {version}")


def test_backward_compatibility():
    """Test that database.emit_event() still works via delegation."""
    print("\n" + "=" * 80)
    print("TEST: Backward Compatibility (database.emit_event)")
    print("=" * 80)
    
    import database
    
    # Call old function (should delegate to boundary)
    event_id = database.emit_event(
        event_type='TEST_LEGACY_CALL',
        quote_id=None,
        event_data={'test': 'backward_compat'}
    )
    
    # Verify event was written with deterministic provenance
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT event_type, ingested_by_service, ingested_by_version FROM cutter__operational_events WHERE id = ?",
        (event_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None, "Event not found"
    assert row[0] == 'TEST_LEGACY_CALL', "Event type mismatch"
    assert row[1] is not None, "ingested_by_service should be populated"
    assert row[2] is not None, "ingested_by_version should be populated"
    
    print(f"[PASS] database.emit_event() delegates correctly")
    print(f"  ingested_by_service: {row[1]}")
    print(f"  ingested_by_version: {row[2]}")


if __name__ == '__main__':
    print("\n")
    print("=" * 80)
    print("CUTTER LEDGER BOUNDARY TEST SUITE")
    print("=" * 80)
    
    try:
        test_only_boundary_writes_to_ledger()
        test_emit_cutter_event_validates()
        test_deterministic_provenance()
        test_explicit_provenance_override()
        test_backward_compatibility()
        
        print("\n" + "=" * 80)
        print("[SUCCESS] ALL BOUNDARY TESTS PASSED")
        print("=" * 80)
        print()
        print("Verified:")
        print("  1. Single write path enforced (only boundary.py)")
        print("  2. Constitutional validation active")
        print("  3. Deterministic provenance (service_id + version)")
        print("  4. Explicit provenance override working")
        print("  5. Backward compatibility maintained")
        print("  6. Debug callsite in event_data (best-effort)")
        print()
        
    except AssertionError as e:
        print("\n" + "=" * 80)
        print(f"[FAIL] {e}")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"[ERROR] {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)
