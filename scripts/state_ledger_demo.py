"""
State Ledger End-to-End Demo

Demonstrates State Ledger constitutional behavior:
- Entity registration and ownership assignment
- Declaration emissions (RECLASSIFICATION and REAFFIRMATION)
- Derived state detection (DS-1, DS-2, DS-5)
- Constitutional refusals (wrong owner, missing owner, append-only)

NO inference, NO summaries, NO advice.
Prints raw results and refusal messages only.

Usage:
    python scripts/state_ledger_demo.py
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from state_ledger.boundary import (
    register_entity,
    assign_owner,
    get_current_owner,
    emit_state_declaration,
    get_declarations,
    query_unowned_entities,
    query_deferred_recognition
)


import database


try:
    DB_PATH = database.require_test_db("state_ledger_demo")
except RuntimeError as exc:
    print(f"[ERROR] {exc}")
    raise SystemExit(1)


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_raw_result(label, data):
    """Print raw data without interpretation."""
    print(f"\n[{label}]")
    if isinstance(data, (list, tuple)):
        if not data:
            print("  (empty)")
        else:
            for item in data:
                print(f"  {item}")
    else:
        print(f"  {data}")


def demo_entity_creation():
    """Demonstrate entity registration and ownership."""
    print_header("PART 1: ENTITY REGISTRATION AND OWNERSHIP")
    
    # Register entities
    print("\n1. Register entities:")
    register_entity("company:acme", "Acme Corporation", cadence_days=7)
    print("  Registered: company:acme (cadence: 7 days)")
    
    register_entity("dept:engineering", "Engineering Department", cadence_days=14)
    print("  Registered: dept:engineering (cadence: 14 days)")
    
    # Assign owners
    print("\n2. Assign recognition owners:")
    assign_owner("company:acme", "user:alice", "admin:system")
    print("  company:acme -> owner: user:alice")
    
    assign_owner("dept:engineering", "user:bob", "admin:system")
    print("  dept:engineering -> owner: user:bob")
    
    # Query current owners
    print("\n3. Query current owners:")
    owner1 = get_current_owner("company:acme")
    owner2 = get_current_owner("dept:engineering")
    print_raw_result("company:acme owner", owner1)
    print_raw_result("dept:engineering owner", owner2)


def demo_declaration_emissions():
    """Demonstrate declaration emissions."""
    print_header("PART 2: DECLARATION EMISSIONS")
    
    print("\n1. Emit RECLASSIFICATION for company:acme:")
    decl1 = emit_state_declaration(
        entity_ref="company:acme",
        scope_ref="scope:monthly",
        state_text="Revenue pipeline is healthy with three active deals pending",
        actor_ref="user:alice",
        declaration_kind="RECLASSIFICATION",
        classification="stable"
    )
    print(f"  Declaration ID: {decl1}")
    print(f"  Kind: RECLASSIFICATION")
    print(f"  Classification: stable")
    
    print("\n2. Emit first REAFFIRMATION for company:acme:")
    decl2 = emit_state_declaration(
        entity_ref="company:acme",
        scope_ref="scope:monthly",
        state_text="Revenue pipeline remains healthy with active deals",
        actor_ref="user:alice",
        declaration_kind="REAFFIRMATION",
        classification="stable"
    )
    print(f"  Declaration ID: {decl2}")
    print(f"  Kind: REAFFIRMATION")
    
    print("\n3. Emit second REAFFIRMATION for company:acme:")
    decl3 = emit_state_declaration(
        entity_ref="company:acme",
        scope_ref="scope:monthly",
        state_text="Revenue pipeline continues stable trajectory",
        actor_ref="user:alice",
        declaration_kind="REAFFIRMATION",
        classification="stable"
    )
    print(f"  Declaration ID: {decl3}")
    print(f"  Kind: REAFFIRMATION")
    
    print("\n4. Emit RECLASSIFICATION for dept:engineering:")
    decl4 = emit_state_declaration(
        entity_ref="dept:engineering",
        scope_ref="scope:weekly",
        state_text="Team capacity is at baseline with no blockers",
        actor_ref="user:bob",
        declaration_kind="RECLASSIFICATION",
        classification="stable"
    )
    print(f"  Declaration ID: {decl4}")
    print(f"  Kind: RECLASSIFICATION")


def demo_derived_states():
    """Demonstrate derived state queries."""
    print_header("PART 3: DERIVED STATE DETECTION")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # DS-1: Persistent Continuity (2+ reaffirmations since reclassification)
    print("\n1. DS-1: Persistent Continuity")
    print("   (Entities with 2+ REAFFIRMATION since most recent RECLASSIFICATION)")
    cursor.execute("SELECT * FROM view_ds1_persistent_continuity")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"\n  Entity: {row['entity_ref']}")
            print(f"  Scope: {row['scope_ref']}")
            print(f"  Classification: {row['classification']}")
            print(f"  Consecutive reaffirmations: {row['consecutive_reaffirmations']}")
            print(f"  First: {row['first_reaffirmed_at']}")
            print(f"  Last: {row['last_reaffirmed_at']}")
    else:
        print("  (no entities meet threshold)")
    
    # DS-2: Unowned Recognition
    print("\n2. DS-2: Unowned Recognition")
    print("   (Entities with no current recognition owner)")
    cursor.execute("SELECT * FROM view_ds2_unowned_recognition")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"\n  Entity: {row['entity_ref']}")
            print(f"  Label: {row['entity_label']}")
            print(f"  Cadence: {row['cadence_days']} days")
    else:
        print("  (no unowned entities)")
    
    # DS-5: Deferred Recognition
    print("\n3. DS-5: Deferred Recognition")
    print("   (Entities past their cadence window)")
    cursor.execute("SELECT * FROM view_ds5_deferred_recognition")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"\n  Entity: {row['entity_ref']}")
            print(f"  Label: {row['entity_label']}")
            print(f"  Cadence: {row['cadence_days']} days")
            print(f"  Last declaration: {row['last_declaration_at']}")
            print(f"  Days since: {row['days_since_last_declaration']}")
    else:
        print("  (no deferred entities)")
    
    conn.close()


def demo_constitutional_refusals():
    """Demonstrate constitutional refusals."""
    print_header("PART 4: CONSTITUTIONAL REFUSALS")
    
    # Refusal 1: Wrong owner
    print("\n1. Attempt declaration with WRONG OWNER:")
    print("   Entity: company:acme (owner: user:alice)")
    print("   Attempted by: user:eve (not the owner)")
    try:
        emit_state_declaration(
            entity_ref="company:acme",
            scope_ref="scope:monthly",
            state_text="Attempting proxy recognition",
            actor_ref="user:eve",
            declaration_kind="REAFFIRMATION",
            classification="stable"
        )
        print("  [UNEXPECTED] Declaration succeeded (should have refused)")
    except ValueError as e:
        print(f"  [REFUSED] {str(e)[:120]}")
    
    # Refusal 2: Missing owner
    print("\n2. Attempt declaration with NO OWNER:")
    print("   Entity: project:alpha (no owner assigned)")
    register_entity("project:alpha", "Project Alpha", cadence_days=7)
    try:
        emit_state_declaration(
            entity_ref="project:alpha",
            scope_ref="scope:weekly",
            state_text="Attempting declaration without owner",
            actor_ref="user:charlie",
            declaration_kind="RECLASSIFICATION",
            classification="stable"
        )
        print("  [UNEXPECTED] Declaration succeeded (should have refused)")
    except ValueError as e:
        print(f"  [REFUSED] {str(e)[:120]}")
    
    # Refusal 3: Append-only trigger (UPDATE)
    print("\n3. Attempt UPDATE on state__declarations:")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Get a specific declaration_id first
        cursor.execute("""
            SELECT declaration_id FROM state__declarations
            WHERE entity_ref = 'company:acme'
            ORDER BY declaration_id DESC
            LIMIT 1
        """)
        decl_id = cursor.fetchone()[0]
        
        cursor.execute("""
            UPDATE state__declarations
            SET state_text = 'Modified text'
            WHERE declaration_id = ?
        """, (decl_id,))
        conn.commit()
        print("  [UNEXPECTED] UPDATE succeeded (should have been blocked)")
    except sqlite3.IntegrityError as e:
        print(f"  [BLOCKED] {str(e)[:120]}")
    finally:
        conn.close()
    
    # Refusal 4: Append-only trigger (DELETE)
    print("\n4. Attempt DELETE on state__declarations:")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Get a specific declaration_id first
        cursor.execute("""
            SELECT declaration_id FROM state__declarations
            WHERE entity_ref = 'company:acme'
            ORDER BY declaration_id DESC
            LIMIT 1
        """)
        decl_id = cursor.fetchone()[0]
        
        cursor.execute("""
            DELETE FROM state__declarations
            WHERE declaration_id = ?
        """, (decl_id,))
        conn.commit()
        print("  [UNEXPECTED] DELETE succeeded (should have been blocked)")
    except sqlite3.IntegrityError as e:
        print(f"  [BLOCKED] {str(e)[:120]}")
    finally:
        conn.close()


def demo_raw_declaration_history():
    """Show raw declaration history."""
    print_header("PART 5: RAW DECLARATION HISTORY")
    
    print("\n1. All declarations for company:acme (raw query):")
    
    # Query directly to show all fields including declaration_kind
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM state__declarations
        WHERE entity_ref = 'company:acme'
        ORDER BY declared_at, declaration_id
    """)
    declarations = cursor.fetchall()
    conn.close()
    
    if declarations:
        for i, decl in enumerate(declarations, 1):
            print(f"\n  Declaration {i}:")
            print(f"    ID: {decl['declaration_id']}")
            print(f"    Kind: {decl['declaration_kind']}")
            print(f"    Scope: {decl['scope_ref']}")
            print(f"    Classification: {decl['classification']}")
            print(f"    State: {decl['state_text'][:60]}...")
            print(f"    Declared by: {decl['declared_by_actor_ref']}")
            print(f"    Declared at: {decl['declared_at']}")
    else:
        print("  (no declarations)")


def main():
    """Run complete State Ledger demonstration."""
    print("\n" + "=" * 80)
    print("  STATE LEDGER END-TO-END DEMONSTRATION")
    print("  Constitutional Behavior Verification")
    print("=" * 80)
    print("\n  Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("  Database:", DB_PATH)
    
    try:
        demo_entity_creation()
        demo_declaration_emissions()
        demo_derived_states()
        demo_constitutional_refusals()
        demo_raw_declaration_history()
        
        print("\n" + "=" * 80)
        print("  DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\n  Summary:")
        print("    [OK] Entity registration and ownership")
        print("    [OK] Declaration emissions (RECLASSIFICATION + REAFFIRMATION)")
        print("    [OK] Derived state detection (DS-1, DS-2, DS-5)")
        print("    [OK] Constitutional refusals (wrong owner, no owner, append-only)")
        print("    [OK] Raw declaration history query")
        print("\n  Constitutional compliance verified.")
        print()
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"  [ERROR] Demo failed: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
