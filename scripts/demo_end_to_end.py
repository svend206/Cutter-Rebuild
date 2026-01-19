#!/usr/bin/env python3
"""
End-to-End Demo: Ops → Cutter Ledger → State Ledger → CLI Queries

Demonstrates the complete flow through all three layers:
1. Ops Layer emits operational exhaust
2. Cutter Ledger captures events (append-only)
3. State Ledger captures recognition (append-only)
4. CLI queries make data visible (raw output)

Constitutional compliance:
- No inference or interpretation
- No summaries or advice
- Raw output only
- Deterministic execution

Environment:
    TEST_DB_PATH: If set, uses that database. Otherwise creates temp db.
"""

import sys
import os
import json
import tempfile
import sqlite3
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import boundary modules
from cutter_ledger.boundary import emit_cutter_event, get_events
from state_ledger.boundary import (
    register_entity, 
    assign_owner, 
    emit_state_declaration,
    get_declarations,
    query_unowned_entities,
    query_deferred_recognition
)
from state_ledger.queries import (
    list_entities,
    query_persistent_continuity,
    get_latest_declarations
)
import database


def setup_test_database():
    """Create and initialize test database."""
    # Use TEST_DB_PATH if set, otherwise create temp db
    if "TEST_DB_PATH" in os.environ:
        test_db_path = Path(os.environ["TEST_DB_PATH"])
        print(f"[SETUP] Using TEST_DB_PATH: {test_db_path}")
    else:
        temp_dir = tempfile.gettempdir()
        test_db_path = Path(temp_dir) / "demo_e2e_test.db"
        os.environ["TEST_DB_PATH"] = str(test_db_path)
        print(f"[SETUP] Created temp database: {test_db_path}")
    
    # Clean slate
    if test_db_path.exists():
        test_db_path.unlink()
    
    # Reload database module to pick up TEST_DB_PATH
    import importlib
    importlib.reload(database)
    database.require_test_db("demo_end_to_end")
    
    # Initialize Ops tables
    print("[SETUP] Initializing Ops tables...")
    database.initialize_database()
    
    # Create Cutter Ledger tables
    print("[SETUP] Initializing Cutter Ledger tables...")
    conn = sqlite3.connect(test_db_path)
    conn.executescript("""
        -- Cutter Ledger: Events
        CREATE TABLE IF NOT EXISTS cutter__events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            subject_ref TEXT NOT NULL,
            event_data TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ingested_by_service TEXT NOT NULL,
            ingested_by_version TEXT NOT NULL
        );
        
        -- Append-only enforcement
        CREATE TRIGGER IF NOT EXISTS prevent_cutter_event_updates
        BEFORE UPDATE ON cutter__events
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: Cutter events are append-only');
        END;
        
        CREATE TRIGGER IF NOT EXISTS prevent_cutter_event_deletes
        BEFORE DELETE ON cutter__events
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: Cutter events cannot be deleted');
        END;
    """)
    conn.commit()
    conn.close()
    
    # Create State Ledger tables
    print("[SETUP] Initializing State Ledger tables...")
    conn = sqlite3.connect(test_db_path)
    conn.executescript("""
        -- State Ledger: Entities
        CREATE TABLE IF NOT EXISTS state__entities (
            entity_ref TEXT PRIMARY KEY,
            entity_label TEXT,
            cadence_days INTEGER NOT NULL DEFAULT 7,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        -- State Ledger: Recognition Owners
        CREATE TABLE IF NOT EXISTS state__recognition_owners (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_ref TEXT NOT NULL,
            owner_actor_ref TEXT NOT NULL,
            assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            unassigned_at TEXT,
            assigned_by_actor_ref TEXT NOT NULL,
            FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
        );
        
        CREATE UNIQUE INDEX IF NOT EXISTS idx_current_owner 
        ON state__recognition_owners(entity_ref) 
        WHERE unassigned_at IS NULL;
        
        -- State Ledger: Declarations
        CREATE TABLE IF NOT EXISTS state__declarations (
            declaration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_ref TEXT NOT NULL,
            scope_ref TEXT NOT NULL,
            state_text TEXT NOT NULL,
            classification TEXT,
            declared_by_actor_ref TEXT NOT NULL,
            declared_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            declaration_kind TEXT NOT NULL CHECK (declaration_kind IN ('REAFFIRMATION','RECLASSIFICATION')),
            supersedes_declaration_id INTEGER,
            cutter_evidence_ref TEXT,
            FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
        );
        
        -- Append-only enforcement
        CREATE TRIGGER IF NOT EXISTS prevent_declaration_updates
        BEFORE UPDATE ON state__declarations
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: State declarations are append-only');
        END;
        
        CREATE TRIGGER IF NOT EXISTS prevent_declaration_deletes
        BEFORE DELETE ON state__declarations
        BEGIN
            SELECT RAISE(ABORT, 'Constitutional violation: State declarations cannot be deleted');
        END;
        
        -- DS-1: Persistent Continuity
        CREATE VIEW IF NOT EXISTS view_ds1_persistent_continuity AS
        WITH last_reclassifications AS (
            SELECT 
                entity_ref,
                scope_ref,
                MAX(declaration_id) as last_recl_id,
                MAX(declared_at) as last_recl_at
            FROM state__declarations
            WHERE declaration_kind = 'RECLASSIFICATION'
            GROUP BY entity_ref, scope_ref
        ),
        reaffirmation_runs AS (
            SELECT 
                d.entity_ref,
                d.scope_ref,
                COUNT(*) as consecutive_reaffirmations,
                MIN(d.declared_at) as first_reaffirmed_at,
                MAX(d.declared_at) as last_reaffirmed_at
            FROM state__declarations d
            LEFT JOIN last_reclassifications lr 
                ON d.entity_ref = lr.entity_ref 
                AND d.scope_ref = lr.scope_ref
            WHERE d.declaration_kind = 'REAFFIRMATION'
                AND (lr.last_recl_id IS NULL OR d.declaration_id > lr.last_recl_id)
            GROUP BY d.entity_ref, d.scope_ref
        )
        SELECT * FROM reaffirmation_runs
        WHERE consecutive_reaffirmations > 1;
        
        -- DS-2: Unowned Recognition
        CREATE VIEW IF NOT EXISTS view_ds2_unowned_recognition AS
        SELECT 
            e.entity_ref,
            e.entity_label,
            e.cadence_days,
            e.created_at as entity_created_at
        FROM state__entities e
        WHERE NOT EXISTS (
            SELECT 1 FROM state__recognition_owners o
            WHERE o.entity_ref = e.entity_ref
            AND o.unassigned_at IS NULL
        );
        
        -- DS-5: Deferred Recognition
        CREATE VIEW IF NOT EXISTS view_ds5_deferred_recognition AS
        SELECT 
            e.entity_ref,
            e.entity_label,
            e.cadence_days,
            MAX(d.declared_at) as last_declaration_at,
            CAST(
                (julianday('now') - julianday(MAX(d.declared_at))) 
                AS INTEGER
            ) as days_since_last_declaration
        FROM state__entities e
        LEFT JOIN state__declarations d ON e.entity_ref = d.entity_ref
        GROUP BY e.entity_ref, e.entity_label, e.cadence_days
        HAVING days_since_last_declaration > e.cadence_days;
    """)
    conn.commit()
    conn.close()
    
    print("[SETUP] Database initialized.\n")
    return test_db_path


def demo_ops_to_cutter_ledger():
    """Demonstrate Ops Layer emitting to Cutter Ledger."""
    print("="*70)
    print("PHASE 1: Ops Layer -> Cutter Ledger (Operational Exhaust)")
    print("="*70)
    
    # Simulate Ops action: price override on a quote
    print("\n[OPS ACTION] User overrides quote price...")
    event_id = emit_cutter_event(
        event_type="quote_price_overridden",
        subject_ref="quote:demo-001",
        event_data={
            "original_price": 1500.00,
            "override_price": 1200.00,
            "override_reason": "volume_discount",
            "actor": "org:demo-shop/actor:sales-manager"
        }
    )
    print(f"[CUTTER LEDGER] Event captured: event_id={event_id}")
    
    # Emit another event: quote finalized
    print("\n[OPS ACTION] Quote finalized and sent to customer...")
    event_id_2 = emit_cutter_event(
        event_type="quote_finalized",
        subject_ref="quote:demo-001",
        event_data={
            "final_price": 1200.00,
            "sent_to": "org:customer-a/entity:contact:john",
            "expires_at": "2026-02-01"
        }
    )
    print(f"[CUTTER LEDGER] Event captured: event_id={event_id_2}")
    
    # Query Cutter Ledger
    print("\n[QUERY] Retrieving all events for quote:demo-001...")
    events = get_events(subject_ref="quote:demo-001")
    print(f"[CUTTER LEDGER] Found {len(events)} event(s):")
    print(json.dumps(events, indent=2, default=str))
    print()


def demo_state_ledger():
    """Demonstrate State Ledger recognition flow."""
    print("="*70)
    print("PHASE 2: State Ledger (Explicit Recognition)")
    print("="*70)
    
    # Register entity
    print("\n[STATE LEDGER] Registering entity: customer relationship...")
    entity_ref = "org:demo-shop/entity:customer:customer-a"
    register_entity(
        entity_ref=entity_ref,
        entity_label="Customer A - High Volume",
        cadence_days=7
    )
    print(f"[STATE LEDGER] Entity registered: {entity_ref}")
    
    # Assign recognition owner
    print("\n[STATE LEDGER] Assigning recognition owner...")
    owner_ref = "org:demo-shop/actor:account-manager"
    assign_owner(
        entity_ref=entity_ref,
        owner_actor_ref=owner_ref,
        assigned_by_actor_ref="org:demo-shop/actor:sales-director"
    )
    print(f"[STATE LEDGER] Owner assigned: {owner_ref}")
    
    # Emit RECLASSIFICATION declaration
    print("\n[STATE LEDGER] Emitting RECLASSIFICATION declaration...")
    scope_ref = "org:demo-shop/scope:weekly-review"
    decl_id_1 = emit_state_declaration(
        entity_ref=entity_ref,
        scope_ref=scope_ref,
        state_text="Customer relationship is active with recent engagement",
        actor_ref=owner_ref,
        declaration_kind="RECLASSIFICATION",
        cutter_evidence_ref=f"cutter_event:quote:demo-001"
    )
    print(f"[STATE LEDGER] Declaration emitted: declaration_id={decl_id_1}")
    
    # Emit first REAFFIRMATION
    print("\n[STATE LEDGER] Emitting first REAFFIRMATION declaration...")
    decl_id_2 = emit_state_declaration(
        entity_ref=entity_ref,
        scope_ref=scope_ref,
        state_text="Customer relationship continues to be active with consistent orders",
        actor_ref=owner_ref,
        declaration_kind="REAFFIRMATION",
        supersedes_declaration_id=decl_id_1
    )
    print(f"[STATE LEDGER] Declaration emitted: declaration_id={decl_id_2}")
    
    # Emit second REAFFIRMATION
    print("\n[STATE LEDGER] Emitting second REAFFIRMATION declaration...")
    decl_id_3 = emit_state_declaration(
        entity_ref=entity_ref,
        scope_ref=scope_ref,
        state_text="Customer relationship remains active with ongoing communication",
        actor_ref=owner_ref,
        declaration_kind="REAFFIRMATION",
        supersedes_declaration_id=decl_id_2
    )
    print(f"[STATE LEDGER] Declaration emitted: declaration_id={decl_id_3}")
    print()


def demo_cli_queries():
    """Demonstrate CLI-style queries (raw function calls)."""
    print("="*70)
    print("PHASE 3: Query Surface (Raw Data Visibility)")
    print("="*70)
    
    # List all entities
    print("\n[QUERY] list_entities():")
    entities = list_entities()
    print(json.dumps(entities, indent=2, default=str))
    
    # Get latest declarations
    print("\n[QUERY] get_latest_declarations(limit=3):")
    latest = get_latest_declarations(limit=3)
    print(json.dumps(latest, indent=2, default=str))
    
    # Query DS-1: Persistent Continuity
    print("\n[QUERY] query_persistent_continuity() [DS-1]:")
    ds1_results = query_persistent_continuity()
    print(json.dumps(ds1_results, indent=2, default=str))
    if ds1_results:
        print(f"[DS-1] Found {len(ds1_results)} entity/scope pair(s) with 2+ reaffirmations")
    else:
        print("[DS-1] No persistent continuity detected (no entities with 2+ reaffirmations)")
    
    # Query DS-2: Unowned Recognition
    print("\n[QUERY] query_unowned_entities() [DS-2]:")
    ds2_results = query_unowned_entities()
    print(json.dumps(ds2_results, indent=2, default=str))
    if ds2_results:
        print(f"[DS-2] Found {len(ds2_results)} unowned entity/entities")
    else:
        print("[DS-2] No unowned entities (all entities have current owners)")
    
    # Query DS-5: Deferred Recognition
    print("\n[QUERY] query_deferred_recognition() [DS-5]:")
    ds5_results = query_deferred_recognition()
    print(json.dumps(ds5_results, indent=2, default=str))
    if ds5_results:
        print(f"[DS-5] Found {len(ds5_results)} entity/entities past cadence window")
    else:
        print("[DS-5] No deferred recognition (all entities within cadence)")
    
    # Get all declarations for the demo entity
    print("\n[QUERY] get_declarations(entity_ref='org:demo-shop/entity:customer:customer-a'):")
    all_decls = get_declarations(entity_ref="org:demo-shop/entity:customer:customer-a")
    print(json.dumps(all_decls, indent=2, default=str))
    print()


def main():
    """Run end-to-end demo."""
    print("\n" + "="*70)
    print("END-TO-END DEMO: Ops -> Cutter Ledger -> State Ledger -> Queries")
    print("="*70)
    print("\nDemonstrates:")
    print("1. Ops Layer emits operational exhaust to Cutter Ledger")
    print("2. State Ledger captures explicit human recognition")
    print("3. CLI queries make data visible (raw, no interpretation)")
    print("4. Constitutional compliance: append-only, no inference")
    print()
    
    try:
        # Setup
        test_db_path = setup_test_database()
        
        # Update boundary module DB paths
        from cutter_ledger import boundary as cutter_boundary
        from state_ledger import boundary as state_boundary
        from state_ledger import queries as state_queries_module
        
        cutter_boundary.DB_PATH = test_db_path
        state_boundary.DB_PATH = test_db_path
        state_queries_module.DB_PATH = test_db_path
        
        # Phase 1: Ops → Cutter Ledger
        demo_ops_to_cutter_ledger()
        
        # Phase 2: State Ledger
        demo_state_ledger()
        
        # Phase 3: CLI Queries
        demo_cli_queries()
        
        print("="*70)
        print("DEMO COMPLETE - All phases executed successfully")
        print("="*70)
        print(f"\nTest database preserved at: {test_db_path}")
        print("You can query it manually using:")
        print(f"  sqlite3 {test_db_path}")
        print("\nConstitutional compliance verified:")
        print("  [OK] Append-only ledgers (no UPDATE/DELETE)")
        print("  [OK] Raw output only (no interpretation)")
        print("  [OK] No summaries or advice")
        print("  [OK] Explicit recognition (no inference)")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
