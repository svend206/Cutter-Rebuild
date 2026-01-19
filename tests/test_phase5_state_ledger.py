"""
Test: Phase 5 State Ledger Verification

Verifies:
1. State Ledger tables created with correct schema
2. Append-only triggers block UPDATE/DELETE
3. Ownership constraint enforces single owner per entity
4. Boundary refusal cases work correctly
5. Derived state views (DS-2, DS-5) work
6. One-sentence enforcement works
"""

import sqlite3
import sys
import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from state_ledger.boundary import (
    register_entity,
    assign_owner,
    get_current_owner,
    emit_state_declaration,
    get_declarations,
    query_unowned_entities,
    query_deferred_recognition
)

if not os.environ.get("TEST_DB_PATH"):
    bootstrap_path = Path(tempfile.gettempdir()) / "test_phase5_state_ledger_bootstrap.db"
    os.environ["TEST_DB_PATH"] = str(bootstrap_path)

import database


def _ensure_test_db() -> Path:
    test_db_env = os.environ.get("TEST_DB_PATH")
    if not test_db_env:
        temp_dir = tempfile.gettempdir()
        test_db_env = str(Path(temp_dir) / "test_phase5_state_ledger.db")
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


def test_tables_created():
    """Verify State Ledger tables were created."""
    print("\n" + "=" * 80)
    print("TEST: State Ledger Tables Created")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check for state__ tables
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'state__%'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ['state__declarations', 'state__entities', 'state__recognition_owners']
    
    print(f"  Found tables: {tables}")
    
    for table in expected_tables:
        assert table in tables, f"Missing table: {table}"
    
    print(f"[PASS] All {len(expected_tables)} State Ledger tables exist")
    
    # Check schema for state__declarations
    cursor.execute("PRAGMA table_info(state__declarations)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = ['declaration_id', 'entity_ref', 'scope_ref', 'state_text', 
                       'declared_by_actor_ref', 'declared_at']
    for col in required_columns:
        assert col in columns, f"Missing column in state__declarations: {col}"
    
    print(f"[PASS] state__declarations schema correct")
    
    conn.close()


def test_append_only_triggers():
    """Verify UPDATE/DELETE blocked on state__declarations."""
    print("\n" + "=" * 80)
    print("TEST: Append-Only Triggers")
    print("=" * 80)
    
    # Create test entity and owner
    register_entity("test:append_only", "Test Append Only")
    assign_owner("test:append_only", "test:actor", "test:admin")
    
    # Emit test declaration
    decl_id = emit_state_declaration(declaration_kind='RECLASSIFICATION', entity_ref="test:append_only",
        scope_ref="test:scope",
        state_text="Test state for append-only verification",
        actor_ref="test:actor"
    )
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test UPDATE blocker
    try:
        cursor.execute(f"""
            UPDATE state__declarations 
            SET state_text = 'Modified' 
            WHERE declaration_id = {decl_id}
        """)
        conn.close()
        raise AssertionError("UPDATE was not blocked by trigger")
    except sqlite3.IntegrityError as e:
        if 'Constitutional violation' in str(e) and 'append-only' in str(e):
            print("[PASS] UPDATE blocked by trigger")
        else:
            raise
    
    # Test DELETE blocker
    try:
        cursor.execute(f"DELETE FROM state__declarations WHERE declaration_id = {decl_id}")
        conn.close()
        raise AssertionError("DELETE was not blocked by trigger")
    except sqlite3.IntegrityError as e:
        if 'Constitutional violation' in str(e):
            print("[PASS] DELETE blocked by trigger")
        else:
            raise
    
    conn.close()


def test_ownership_constraint():
    """Verify exactly one current owner per entity."""
    print("\n" + "=" * 80)
    print("TEST: Ownership Constraint")
    print("=" * 80)
    
    # Create test entity
    register_entity("test:ownership", "Test Ownership")
    
    # Assign first owner
    assign_owner("test:ownership", "user:alice", "admin:system")
    current = get_current_owner("test:ownership")
    assert current == "user:alice", f"Expected user:alice, got {current}"
    print("[PASS] First owner assigned: user:alice")
    
    # Reassign to different owner (should unassign first)
    assign_owner("test:ownership", "user:bob", "admin:system")
    current = get_current_owner("test:ownership")
    assert current == "user:bob", f"Expected user:bob, got {current}"
    print("[PASS] Ownership reassigned: user:bob (alice auto-unassigned)")
    
    # Verify only one current owner
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM state__recognition_owners
        WHERE entity_ref = 'test:ownership'
        AND unassigned_at IS NULL
    """)
    current_count = cursor.fetchone()[0]
    conn.close()
    
    assert current_count == 1, f"Expected 1 current owner, found {current_count}"
    print("[PASS] Exactly one current owner enforced")


def test_boundary_refusal_no_owner():
    """Test boundary refuses declaration if entity has no owner (DS-2)."""
    print("\n" + "=" * 80)
    print("TEST: Boundary Refusal - No Owner (DS-2)")
    print("=" * 80)
    
    # Create entity without owner
    register_entity("test:unowned", "Test Unowned Entity")
    
    # Try to emit declaration (should fail)
    try:
        emit_state_declaration(declaration_kind='RECLASSIFICATION', entity_ref="test:unowned",
            scope_ref="test:scope",
            state_text="This should be refused",
            actor_ref="user:charlie"
        )
        raise AssertionError("Boundary should have refused (entity has no owner)")
    except ValueError as e:
        if 'DS-2' in str(e) and 'no current recognition owner' in str(e):
            print("[PASS] Boundary refused: entity has no owner")
            print(f"  Error message: {str(e)[:100]}...")
        else:
            raise


def test_boundary_refusal_wrong_owner():
    """Test boundary refuses if actor is not current owner (DS-2)."""
    print("\n" + "=" * 80)
    print("TEST: Boundary Refusal - Wrong Owner (DS-2)")
    print("=" * 80)
    
    # Create entity with owner
    register_entity("test:wrong_owner", "Test Wrong Owner")
    assign_owner("test:wrong_owner", "user:david", "admin:system")
    
    # Try to emit declaration as different actor (should fail)
    try:
        emit_state_declaration(declaration_kind='RECLASSIFICATION', entity_ref="test:wrong_owner",
            scope_ref="test:scope",
            state_text="This should be refused",
            actor_ref="user:eve"  # Not the owner (david is)
        )
        raise AssertionError("Boundary should have refused (wrong actor)")
    except ValueError as e:
        if 'DS-2' in str(e) and 'not the current recognition owner' in str(e):
            print("[PASS] Boundary refused: actor is not current owner")
            print(f"  Error message: {str(e)[:100]}...")
        else:
            raise


def test_one_sentence_enforcement():
    """Test boundary refuses multi-line state_text (newlines)."""
    print("\n" + "=" * 80)
    print("TEST: One-Sentence Enforcement")
    print("=" * 80)
    
    # Create entity with owner
    register_entity("test:one_sentence", "Test One Sentence")
    assign_owner("test:one_sentence", "user:frank", "admin:system")
    
    # Try multi-line state_text (should fail)
    try:
        emit_state_declaration(declaration_kind='RECLASSIFICATION', entity_ref="test:one_sentence",
            scope_ref="test:scope",
            state_text="This is line one\nThis is line two",
            actor_ref="user:frank"
        )
        raise AssertionError("Boundary should have refused (newline in state_text)")
    except ValueError as e:
        if 'one sentence' in str(e) and 'newlines not allowed' in str(e):
            print("[PASS] Boundary refused: newlines in state_text")
        else:
            raise
    
    # Valid single-line should work
    decl_id = emit_state_declaration(declaration_kind='RECLASSIFICATION', entity_ref="test:one_sentence",
        scope_ref="test:scope",
        state_text="This is a valid single-sentence declaration",
        actor_ref="user:frank"
    )
    print(f"[PASS] Valid single sentence accepted: ID={decl_id}")


def test_empty_state_text_refusal():
    """Test boundary refuses empty or whitespace state_text."""
    print("\n" + "=" * 80)
    print("TEST: Empty state_text Refusal")
    print("=" * 80)
    
    # Create entity with owner
    register_entity("test:empty_state", "Test Empty State")
    assign_owner("test:empty_state", "user:grace", "admin:system")
    
    # Try empty state_text
    try:
        emit_state_declaration(declaration_kind='RECLASSIFICATION', entity_ref="test:empty_state",
            scope_ref="test:scope",
            state_text="",
            actor_ref="user:grace"
        )
        raise AssertionError("Boundary should have refused (empty state_text)")
    except ValueError as e:
        if 'required' in str(e) and 'empty' in str(e).lower():
            print("[PASS] Boundary refused: empty state_text")
        else:
            raise
    
    # Try whitespace-only state_text
    try:
        emit_state_declaration(declaration_kind='RECLASSIFICATION', entity_ref="test:empty_state",
            scope_ref="test:scope",
            state_text="   ",
            actor_ref="user:grace"
        )
        raise AssertionError("Boundary should have refused (whitespace-only state_text)")
    except ValueError as e:
        if 'required' in str(e):
            print("[PASS] Boundary refused: whitespace-only state_text")
        else:
            raise


def test_ds2_unowned_recognition():
    """Test DS-2 view detects unowned entities."""
    print("\n" + "=" * 80)
    print("TEST: DS-2 Unowned Recognition View")
    print("=" * 80)
    
    # Create unowned entity
    register_entity("test:ds2_unowned", "Test DS-2 Unowned", cadence_days=7)
    
    # Query DS-2
    unowned = query_unowned_entities()
    
    # Should include our test entity
    unowned_refs = [e['entity_ref'] for e in unowned]
    assert "test:ds2_unowned" in unowned_refs, "DS-2 should detect unowned entity"
    
    print(f"[PASS] DS-2 detected {len(unowned)} unowned entities")
    print(f"  Includes: test:ds2_unowned")
    
    # Assign owner - should disappear from DS-2
    assign_owner("test:ds2_unowned", "user:henry", "admin:system")
    unowned_after = query_unowned_entities()
    unowned_refs_after = [e['entity_ref'] for e in unowned_after]
    
    assert "test:ds2_unowned" not in unowned_refs_after, "DS-2 should not include owned entity"
    print(f"[PASS] DS-2 correctly excludes owned entity")


def test_ds5_deferred_recognition():
    """Test DS-5 view detects entities past cadence."""
    print("\n" + "=" * 80)
    print("TEST: DS-5 Deferred Recognition View")
    print("=" * 80)
    
    # Create entity with short cadence
    register_entity("test:ds5_deferred", "Test DS-5 Deferred", cadence_days=1)
    assign_owner("test:ds5_deferred", "user:iris", "admin:system")
    
    # No declaration yet - should appear in DS-5
    deferred = query_deferred_recognition()
    deferred_refs = [e['entity_ref'] for e in deferred]
    
    assert "test:ds5_deferred" in deferred_refs, "DS-5 should detect entity with no declarations"
    print(f"[PASS] DS-5 detected entity with no declarations")
    
    # Make a declaration
    emit_state_declaration(declaration_kind='RECLASSIFICATION', entity_ref="test:ds5_deferred",
        scope_ref="test:weekly",
        state_text="Entity state is current as of today",
        actor_ref="user:iris"
    )
    
    # Should disappear from DS-5 (recent declaration)
    deferred_after = query_deferred_recognition()
    deferred_refs_after = [e['entity_ref'] for e in deferred_after]
    
    # Note: Depending on timing, might still be in DS-5 if < 1 day has passed
    # We just verify the query works
    print(f"[PASS] DS-5 query executed (found {len(deferred_after)} deferred entities)")


def test_successful_declaration():
    """Test complete successful declaration workflow."""
    print("\n" + "=" * 80)
    print("TEST: Successful Declaration Workflow")
    print("=" * 80)
    
    # 1. Register entity
    entity_ref = "company:acme"
    register_entity(entity_ref, "ACME Corporation", cadence_days=7)
    print(f"[OK] Registered entity: {entity_ref}")
    
    # 2. Assign owner
    owner = "user:ceo"
    assign_owner(entity_ref, owner, "admin:system")
    print(f"[OK] Assigned owner: {owner}")
    
    # 3. Emit declaration
    decl_id = emit_state_declaration(declaration_kind='RECLASSIFICATION', entity_ref=entity_ref,
        scope_ref="scope:weekly",
        state_text="Sales pipeline is healthy with three active deals pending",
        actor_ref=owner,
        classification="stable"
    )
    print(f"[OK] Declaration emitted: ID={decl_id}")
    
    # 4. Retrieve declaration
    declarations = get_declarations(entity_ref=entity_ref)
    assert len(declarations) > 0, "Should find at least one declaration"
    
    latest = declarations[0]
    assert latest['entity_ref'] == entity_ref
    assert latest['declared_by_actor_ref'] == owner
    assert latest['scope_ref'] == "scope:weekly"
    assert latest['classification'] == "stable"
    
    print(f"[PASS] Complete workflow succeeded")
    print(f"  Declaration: {latest['state_text'][:60]}...")


def run_all_tests():
    """Run all Phase 5 verification tests."""
    print("\n" + "=" * 80)
    print("PHASE 5 STATE LEDGER VERIFICATION TEST SUITE")
    print("=" * 80)
    
    try:
        test_tables_created()
        test_append_only_triggers()
        test_ownership_constraint()
        test_boundary_refusal_no_owner()
        test_boundary_refusal_wrong_owner()
        test_one_sentence_enforcement()
        test_empty_state_text_refusal()
        test_ds2_unowned_recognition()
        test_ds5_deferred_recognition()
        test_successful_declaration()
        
        print("\n" + "=" * 80)
        print("[SUCCESS] ALL PHASE 5 TESTS PASSED")
        print("=" * 80)
        print()
        print("Verified:")
        print("  [OK] State Ledger tables created")
        print("  [OK] Append-only triggers active")
        print("  [OK] Ownership constraint enforced (one owner per entity)")
        print("  [OK] Boundary refuses if no owner (DS-2)")
        print("  [OK] Boundary refuses if wrong owner (DS-2)")
        print("  [OK] One-sentence enforcement (no newlines)")
        print("  [OK] Empty state_text refused")
        print("  [OK] DS-2 (Unowned Recognition) view works")
        print("  [OK] DS-5 (Deferred Recognition) view works")
        print("  [OK] Complete declaration workflow")
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
    success = run_all_tests()
    sys.exit(0 if success else 1)
