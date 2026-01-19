"""
State Ledger Query Functions (Read-Only)

Additional query functions for CLI and programmatic access.
See state_ledger/boundary.py for core query functions.
"""

import sqlite3
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


# Support TEST_DB_PATH for hermetic testing
DB_PATH = Path(os.environ.get("TEST_DB_PATH", "cutter.db"))


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def list_entities() -> List[Dict[str, Any]]:
    """
    List all registered entities in the State Ledger.
    
    Returns raw entity registry data (no inference, no recommendations).
    
    Returns:
        List of entity dicts with entity_ref, entity_label, cadence_days, created_at
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT entity_ref, entity_label, cadence_days, created_at
        FROM state__entities
        ORDER BY created_at DESC
    """)
    
    entities = []
    for row in cursor.fetchall():
        entities.append({
            'entity_ref': row['entity_ref'],
            'entity_label': row['entity_label'],
            'cadence_days': row['cadence_days'],
            'created_at': row['created_at']
        })
    
    conn.close()
    return entities


def query_persistent_continuity() -> List[Dict[str, Any]]:
    """
    Query DS-1: Persistent Continuity.
    
    Returns entities with 2+ explicit reaffirmations since most recent reclassification.
    
    Constitutional Note:
    - This is structural visibility, not an alert
    - No inference or recommendation provided
    - No scoring or prioritization applied
    - Returns raw data for human judgment
    
    Returns:
        List of dicts with entity_ref, scope_ref, consecutive_reaffirmations, 
        first_reaffirmed_at, last_reaffirmed_at
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM view_ds1_persistent_continuity")
    
    entities = []
    for row in cursor.fetchall():
        entities.append({
            'entity_ref': row['entity_ref'],
            'scope_ref': row['scope_ref'],
            'consecutive_reaffirmations': row['consecutive_reaffirmations'],
            'first_reaffirmed_at': row['first_reaffirmed_at'],
            'last_reaffirmed_at': row['last_reaffirmed_at']
        })
    
    conn.close()
    return entities


def get_latest_declarations(
    entity_ref: Optional[str] = None,
    scope_ref: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get latest declarations (most recent first).
    
    This is a convenience wrapper for common CLI usage.
    For full filtering options, use state_ledger.boundary.get_declarations().
    
    Args:
        entity_ref: Filter by entity (optional)
        scope_ref: Filter by scope (optional)
        limit: Maximum results (default: 10)
    
    Returns:
        List of declaration dicts
    """
    from state_ledger.boundary import get_declarations
    
    return get_declarations(
        entity_ref=entity_ref,
        scope_ref=scope_ref,
        limit=limit
    )


def query_open_deadlines(
    db_path: Optional[Path] = None,
    conn: Optional[sqlite3.Connection] = None
) -> List[Dict[str, Any]]:
    """
    Query open promise:deadline declarations with no carrier_handoff event.

    Returns raw declaration data only (no inference, no scoring, no prioritization).
    """
    owns_conn = False
    if conn is None:
        if db_path is not None:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            owns_conn = True
        else:
            conn = get_connection()
            owns_conn = True
    cursor = conn.cursor()

    cursor.execute("""
        SELECT d.entity_ref, d.state_text, d.declared_at, d.declared_by_actor_ref
        FROM state__declarations d
        WHERE d.scope_ref = 'promise:deadline'
        AND NOT EXISTS (
            SELECT 1
            FROM cutter__events e
            WHERE e.event_type = 'carrier_handoff'
            AND e.subject_ref = d.entity_ref
        )
        ORDER BY d.declared_at ASC
    """)

    results = []
    for row in cursor.fetchall():
        try:
            payload = json.loads(row['state_text'])
        except json.JSONDecodeError as exc:
            if owns_conn:
                conn.close()
            raise ValueError(f"Malformed state_text JSON for {row['entity_ref']}: {exc}") from exc

        if not isinstance(payload, dict) or 'deadline' not in payload:
            if owns_conn:
                conn.close()
            raise ValueError(f"Missing deadline in state_text for {row['entity_ref']}")

        results.append({
            'entity_ref': row['entity_ref'],
            'deadline': payload['deadline'],
            'declared_at': row['declared_at'],
            'declared_by_actor_ref': row['declared_by_actor_ref'],
        })

    if owns_conn:
        conn.close()
    return results
