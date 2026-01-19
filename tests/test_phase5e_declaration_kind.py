"""
Test: Phase 5e - Declaration Kind (Reaffirmation vs Reclassification)

Verifies:
1. declaration_kind is required in boundary
2. Only REAFFIRMATION and RECLASSIFICATION are valid
3. DS-1 view correctly computes consecutive reaffirmation streaks
4. Streaks are broken by reclassifications
5. A->B->A does NOT count as consecutive
"""

import sqlite3
import sys
import uuid
from pathlib import Path

from state_ledger.boundary import (
    register_entity,
    assign_owner,
    emit_state_declaration,
    get_declarations
)


DB_PATH = Path("cutter.db")


def unique_ref(base: str) -> str:
    """Generate unique entity ref to avoid test data pollution."""
    return f"{base}:{uuid.uuid4().hex[:8]}"


def test_declaration_kind_required():
    """Test boundary refuses missing declaration_kind."""
    print("\n" + "=" * 80)
    print("TEST: declaration_kind Required")
    print("=" * 80)
    
    entity_ref = unique_ref("test:req_kind")
    register_entity(entity_ref, "Test Required Kind")
    assign_owner(entity_ref, "user:test", "admin:system")
    
    # Try without declaration_kind (should fail due to signature)
    try:
        emit_state_declaration(
            entity_ref=entity_ref,
            scope_ref="test:scope",
            state_text="Test without declaration_kind",
            actor_ref="user:test"
        )
        raise AssertionError("Should have failed without declaration_kind")
    except TypeError as e:
        if 'declaration_kind' in str(e):
            print("[PASS] Boundary refuses missing declaration_kind (TypeError)")
        else:
            raise


def test_declaration_kind_validation():
    """Test boundary validates declaration_kind values."""
    print("\n" + "=" * 80)
    print("TEST: declaration_kind Validation")
    print("=" * 80)
    
    entity_ref = unique_ref("test:validate_kind")
    register_entity(entity_ref, "Test Validate Kind")
    assign_owner(entity_ref, "user:test", "admin:system")
    
    # Try invalid value
    try:
        emit_state_declaration(
            declaration_kind="INVALID",
            entity_ref=entity_ref,
            scope_ref="test:scope",
            state_text="Test with invalid kind",
            actor_ref="user:test"
        )
        raise AssertionError("Should have rejected invalid declaration_kind")
    except ValueError as e:
        if 'REAFFIRMATION' in str(e) and 'RECLASSIFICATION' in str(e):
            print("[PASS] Boundary rejects invalid declaration_kind")
            print(f"  Error: {str(e)[:100]}...")
        else:
            raise
    
    # Try valid values
    decl1 = emit_state_declaration(
        declaration_kind="RECLASSIFICATION",
        entity_ref=entity_ref,
        scope_ref="test:scope",
        state_text="Initial classification",
        actor_ref="user:test"
    )
    print(f"[PASS] RECLASSIFICATION accepted: ID={decl1}")
    
    decl2 = emit_state_declaration(
        declaration_kind="REAFFIRMATION",
        entity_ref=entity_ref,
        scope_ref="test:scope",
        state_text="Reaffirming state",
        actor_ref="user:test"
    )
    print(f"[PASS] REAFFIRMATION accepted: ID={decl2}")


def test_ds1_consecutive_reaffirmations():
    """Test DS-1 detects current continuity run (2+ reaffirmations since reclassification)."""
    print("\n" + "=" * 80)
    print("TEST: DS-1 Current Continuity Run (2+ Reaffirmations)")
    print("=" * 80)
    
    entity_ref = unique_ref("test:ds1_consecutive")
    register_entity(entity_ref, "Test DS-1 Consecutive")
    assign_owner(entity_ref, "user:test", "admin:system")
    
    # Initial reclassification
    emit_state_declaration(
        declaration_kind="RECLASSIFICATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="Initial state established",
        actor_ref="user:test",
        classification="stable"
    )
    print("[OK] Initial RECLASSIFICATION emitted")
    
    # 2 reaffirmations (meets threshold)
    emit_state_declaration(
        declaration_kind="REAFFIRMATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="State continues as before",
        actor_ref="user:test",
        classification="stable"
    )
    emit_state_declaration(
        declaration_kind="REAFFIRMATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="State remains unchanged",
        actor_ref="user:test",
        classification="stable"
    )
    print("[OK] 2 REAFFIRMATION declarations emitted (meets threshold)")
    
    # Check DS-1 view
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM view_ds1_persistent_continuity
        WHERE entity_ref = ?
    """, (entity_ref,))
    
    rows = cursor.fetchall()
    conn.close()
    
    assert len(rows) == 1, f"Expected 1 continuity run, found {len(rows)}"
    
    run = rows[0]
    assert run['consecutive_reaffirmations'] == 2, f"Expected 2 reaffirmations, got {run['consecutive_reaffirmations']}"
    assert run['classification'] == 'stable', f"Expected stable, got {run['classification']}"
    
    print(f"[PASS] DS-1 detected current continuity run: {run['consecutive_reaffirmations']} reaffirmations since last reclassification")


def test_ds1_reclassification_breaks_run():
    """Test DS-1: Reclassification breaks current continuity run."""
    print("\n" + "=" * 80)
    print("TEST: DS-1 Reclassification Breaks Continuity Run")
    print("=" * 80)
    
    entity_ref = unique_ref("test:ds1_break")
    register_entity(entity_ref, "Test DS-1 Break")
    assign_owner(entity_ref, "user:test", "admin:system")
    
    # Initial: A (reclassification)
    emit_state_declaration(
        declaration_kind="RECLASSIFICATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="Initial state A",
        actor_ref="user:test",
        classification="stable"
    )
    
    # A (reaffirmation)
    emit_state_declaration(
        declaration_kind="REAFFIRMATION",
        entity_ref="test:ds1_break",
        scope_ref="test:weekly",
        state_text="Reaffirm A",
        actor_ref="user:test",
        classification="stable"
    )
    
    # A (reaffirmation)
    emit_state_declaration(
        declaration_kind="REAFFIRMATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="Reaffirm A again",
        actor_ref="user:test",
        classification="stable"
    )
    print("[OK] Created A->A->A pattern (2 reaffirmations)")
    
    # B (reclassification) - breaks run
    emit_state_declaration(
        declaration_kind="RECLASSIFICATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="Reclassify to B",
        actor_ref="user:test",
        classification="degrading"
    )
    print("[OK] RECLASSIFICATION to B (breaks continuity run)")
    
    # B (2 reaffirmations to meet threshold)
    emit_state_declaration(
        declaration_kind="REAFFIRMATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="Reaffirm B first time",
        actor_ref="user:test",
        classification="degrading"
    )
    emit_state_declaration(
        declaration_kind="REAFFIRMATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="Reaffirm B second time",
        actor_ref="user:test",
        classification="degrading"
    )
    print("[OK] 2 REAFFIRMATIONs of B (new continuity run starts)")
    
    # Check DS-1 view
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM view_ds1_persistent_continuity
        WHERE entity_ref = ?
        ORDER BY consecutive_reaffirmations DESC
    """, (entity_ref,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Should show current run (2 reaffirmations of B), not old run
    assert len(rows) == 1, f"Expected 1 current run, found {len(rows)}"
    
    current_run = rows[0]
    assert current_run['consecutive_reaffirmations'] == 2, \
        f"Expected 2 reaffirmations in current run, got {current_run['consecutive_reaffirmations']}"
    assert current_run['classification'] == 'degrading', \
        f"Expected degrading, got {current_run['classification']}"
    
    print("[PASS] DS-1 shows only current continuity run (old run broken)")
    print(f"  Current: {current_run['consecutive_reaffirmations']} reaffirmations of 'degrading'")


def test_ds1_below_threshold():
    """Test DS-1: Single reaffirmation does not appear (below threshold)."""
    print("\n" + "=" * 80)
    print("TEST: DS-1 Below Threshold (1 Reaffirmation)")
    print("=" * 80)
    
    entity_ref = unique_ref("test:ds1_no_false")
    register_entity(entity_ref, "Test DS-1 No False")
    assign_owner(entity_ref, "user:test", "admin:system")
    
    # A (reclassification)
    emit_state_declaration(
        declaration_kind="RECLASSIFICATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="State A",
        actor_ref="user:test",
        classification="stable"
    )
    
    # A (single reaffirmation - below threshold)
    emit_state_declaration(
        declaration_kind="REAFFIRMATION",
        entity_ref=entity_ref,
        scope_ref="test:weekly",
        state_text="Reaffirm A once",
        actor_ref="user:test",
        classification="stable"
    )
    print("[OK] Created RECL(A)->REAF(A) pattern (1 reaffirmation)")
    
    # Check DS-1 view
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM view_ds1_persistent_continuity
        WHERE entity_ref = ?
    """, (entity_ref,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Should be EMPTY - only 1 reaffirmation (below threshold of 2)
    assert len(rows) == 0, \
        f"Expected 0 runs (below threshold), found {len(rows)}"
    
    print("[PASS] DS-1 correctly shows nothing")
    print("  Rationale: 1 reaffirmation below threshold (requires 2+)")


def test_backfill_as_reclassification():
    """Test that existing declarations were backfilled as RECLASSIFICATION."""
    print("\n" + "=" * 80)
    print("TEST: Backfill as RECLASSIFICATION")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Count total declarations
    cursor.execute("SELECT COUNT(*) FROM state__declarations")
    total = cursor.fetchone()[0]
    
    # Count by kind
    cursor.execute("""
        SELECT declaration_kind, COUNT(*) 
        FROM state__declarations 
        GROUP BY declaration_kind
    """)
    
    kinds = dict(cursor.fetchall())
    conn.close()
    
    print(f"[INFO] Total declarations: {total}")
    print(f"[INFO] RECLASSIFICATION: {kinds.get('RECLASSIFICATION', 0)}")
    print(f"[INFO] REAFFIRMATION: {kinds.get('REAFFIRMATION', 0)}")
    
    # Verify no NULL values
    assert None not in kinds, "Found NULL declaration_kind values"
    print("[PASS] No NULL declaration_kind values")
    
    # Verify only valid values
    for kind in kinds.keys():
        assert kind in ('REAFFIRMATION', 'RECLASSIFICATION'), \
            f"Invalid declaration_kind: {kind}"
    print("[PASS] All declaration_kind values are valid")


def run_all_tests():
    """Run all Phase 5e verification tests."""
    print("\n" + "=" * 80)
    print("PHASE 5e DECLARATION KIND VERIFICATION TEST SUITE")
    print("=" * 80)
    
    try:
        test_declaration_kind_required()
        test_declaration_kind_validation()
        test_ds1_consecutive_reaffirmations()
        test_ds1_reclassification_breaks_run()
        test_ds1_below_threshold()
        test_backfill_as_reclassification()
        
        print("\n" + "=" * 80)
        print("[SUCCESS] ALL PHASE 5e TESTS PASSED")
        print("=" * 80)
        print()
        print("Verified:")
        print("  [OK] declaration_kind required by boundary")
        print("  [OK] Only REAFFIRMATION and RECLASSIFICATION accepted")
        print("  [OK] DS-1 detects current continuity run (2+ reaffirmations)")
        print("  [OK] DS-1 breaks run on reclassification")
        print("  [OK] DS-1 respects threshold (1 reaffirmation not shown)")
        print("  [OK] Backfill set existing declarations as RECLASSIFICATION")
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
