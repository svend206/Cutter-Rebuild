"""
State Ledger Boundary - Single Authorized Write Path

This module is the ONLY location permitted to INSERT into state__declarations.
All state recognition must pass through emit_state_declaration().

Constitutional Enforcement:
- DS-2 (Unowned Recognition): Refuses if entity has no current owner
- DS-2 (No Proxy Recognition): Refuses if actor is not the owner
- DS-5 (Deferred Recognition): Tracks cadence for recognition gaps
- C4 (Irreversible Memory): Append-only (no UPDATE/DELETE by triggers)
- C5 (Separation of Observation and Judgment): No interpretation

Critical Refusals:
- No auto-generation of declarations from other ledgers
- No default acknowledgment or pre-filled state
- No silent continuity (no carry-forward)
- No proxy recognition (only owner can declare)

CRITICAL: No other module should write to state__declarations directly.
"""

import os
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from . import validation


def _get_db_path() -> Path:
    """Get database path (respects TEST_DB_PATH environment variable)."""
    test_db_path = os.environ.get('TEST_DB_PATH')
    if test_db_path:
        return Path(test_db_path)
    return Path("cutter.db")


def get_connection() -> sqlite3.Connection:
    """
    Get database connection with foreign keys enabled.
    Respects TEST_DB_PATH environment variable for hermetic testing.
    """
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def register_entity(
    entity_ref: str,
    entity_label: Optional[str] = None,
    cadence_days: int = 7
) -> bool:
    """
    Register an entity in the State Ledger registry.
    
    Args:
        entity_ref: Guild-safe entity reference (format: org:{domain}/entity:{type}:{id})
        entity_label: Optional human-readable label
        cadence_days: Expected reaffirmation cadence (default: 7 days)
    
    Returns:
        True if registered, False if already exists
    
    Raises:
        ValueError: If entity_ref format invalid or cadence_days < 1
    """
    # Validate entity_ref format (Guild-safe identifier)
    is_valid, error_msg = validation.validate_entity_ref(entity_ref)
    if not is_valid:
        raise ValueError(f"Invalid entity_ref: {error_msg}")
    
    if cadence_days < 1:
        raise ValueError(f"cadence_days must be >= 1, got: {cadence_days}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO state__entities (entity_ref, entity_label, cadence_days)
            VALUES (?, ?, ?)
        """, (entity_ref, entity_label, cadence_days))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Entity already exists
        conn.close()
        return False


def get_current_owner(entity_ref: str) -> Optional[str]:
    """
    Get the current recognition owner for an entity.
    
    Args:
        entity_ref: Entity reference
    
    Returns:
        owner_actor_ref if entity has current owner, None if unowned
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT owner_actor_ref
        FROM state__recognition_owners
        WHERE entity_ref = ?
        AND unassigned_at IS NULL
    """, (entity_ref,))
    
    row = cursor.fetchone()
    conn.close()
    
    return row['owner_actor_ref'] if row else None


def assign_owner(
    entity_ref: str,
    owner_actor_ref: str,
    assigned_by_actor_ref: str
) -> int:
    """
    Assign a recognition owner to an entity.
    
    Constitutional Enforcement (DS-2):
    - Exactly one current owner per entity (no committee recognition)
    - If entity has current owner, that owner is unassigned explicitly
    - No silent continuity: ownership changes are recorded, not assumed
    
    Args:
        entity_ref: Guild-safe entity reference
        owner_actor_ref: Guild-safe actor reference being assigned as owner
        assigned_by_actor_ref: Guild-safe actor performing the assignment
    
    Returns:
        Assignment record ID
    
    Raises:
        ValueError: If entity_ref or actor_refs are invalid (format or empty)
        sqlite3.IntegrityError: If entity doesn't exist
    """
    # Validate identifier formats (Guild-safe conventions)
    entity_valid, entity_error = validation.validate_entity_ref(entity_ref)
    if not entity_valid:
        raise ValueError(f"Invalid entity_ref: {entity_error}")
    
    owner_valid, owner_error = validation.validate_actor_ref(owner_actor_ref)
    if not owner_valid:
        raise ValueError(f"Invalid owner_actor_ref: {owner_error}")
    
    assigner_valid, assigner_error = validation.validate_actor_ref(assigned_by_actor_ref)
    if not assigner_valid:
        raise ValueError(f"Invalid assigned_by_actor_ref: {assigner_error}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Unassign current owner if exists
        cursor.execute("""
            UPDATE state__recognition_owners
            SET unassigned_at = CURRENT_TIMESTAMP
            WHERE entity_ref = ?
            AND unassigned_at IS NULL
        """, (entity_ref,))
        
        # Assign new owner
        cursor.execute("""
            INSERT INTO state__recognition_owners 
            (entity_ref, owner_actor_ref, assigned_by_actor_ref)
            VALUES (?, ?, ?)
        """, (entity_ref, owner_actor_ref, assigned_by_actor_ref))
        
        assignment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return assignment_id
        
    except sqlite3.IntegrityError as e:
        conn.close()
        raise ValueError(f"Failed to assign owner: {e}")


def emit_state_declaration(
    entity_ref: str,
    scope_ref: str,
    state_text: str,
    actor_ref: str,
    declaration_kind: str,
    cutter_evidence_ref: Optional[str] = None,
    evidence_refs: Optional[list] = None,
    supersedes_declaration_id: Optional[int] = None
) -> int:
    """
    Emit an explicit state declaration to the State Ledger (append-only).
    
    This is the ONLY authorized write path into state__declarations.
    
    CONSTITUTIONAL ENFORCEMENTS:
    - DS-2 (Unowned Recognition): Refuses if entity has no current owner
    - DS-2 (No Proxy Recognition): Refuses if actor is not the current owner
    - C4 (Irreversible Memory): Append-only (no UPDATE/DELETE by triggers)
    - C5 (Separation of Observation): No interpretation, just declaration
    - DS-1 (Persistent Continuity): Explicit declaration_kind required
    - No auto-generation: Must be explicit human declaration
    - No default acknowledgment: No pre-filled or suggested state
    - No silent continuity: No carry-forward from previous declarations
    
    MECHANICAL ENFORCEMENTS:
    - Refuses empty or whitespace state_text
    - Refuses newline in state_text (forces one sentence, atomic declaration)
    - Refuses missing required fields (entity_ref, scope_ref, actor_ref, declaration_kind)
    - Refuses invalid declaration_kind (must be REAFFIRMATION or RECLASSIFICATION)
    - Validates Guild-safe identifier formats (entity_ref, scope_ref, actor_ref)
    
    Args:
        entity_ref: Guild-safe entity reference (must be registered)
        scope_ref: Guild-safe scope reference
        state_text: One sentence, present tense declaration
        actor_ref: Guild-safe actor making the declaration (must be current owner)
        declaration_kind: REAFFIRMATION or RECLASSIFICATION (explicit, required)
        classification: Optional classification (minimal vocabulary)
        cutter_evidence_ref: Optional reference to Cutter Ledger event
        evidence_refs: Optional list of evidence references (stored inert)
        supersedes_declaration_id: Optional pointer to previous declaration
    
    Returns:
        Declaration ID (integer)
    
    Raises:
        ValueError: If validation fails or actor is not current owner
    """
    # Validate Guild-safe identifier formats first
    refs_valid, refs_error = validation.validate_all_refs(entity_ref, actor_ref, scope_ref)
    if not refs_valid:
        raise ValueError(f"Identifier format validation failed: {refs_error}")
    
    # Validate state_text presence
    if not state_text or not state_text.strip():
        raise ValueError("state_text is required (cannot be empty or whitespace)")
    
    # Validate declaration_kind
    if not declaration_kind or not declaration_kind.strip():
        raise ValueError("declaration_kind is required (REAFFIRMATION or RECLASSIFICATION)")
    
    # Validate declaration_kind
    if declaration_kind not in ('REAFFIRMATION', 'RECLASSIFICATION'):
        raise ValueError(
            f"declaration_kind must be 'REAFFIRMATION' or 'RECLASSIFICATION', got: {declaration_kind}. "
            "Constitutional requirement (DS-1): Explicit declaration of continuity vs change."
        )
    
    # Mechanical enforcement: one sentence (no newlines)
    if '\n' in state_text or '\r' in state_text:
        raise ValueError(
            "state_text must be one sentence (newlines not allowed). "
            "Constitutional requirement: explicit, atomic declarations."
        )

    evidence_refs_json = None
    if evidence_refs is not None:
        if not isinstance(evidence_refs, list):
            raise ValueError("evidence_refs must be a list when provided")
        try:
            evidence_refs_json = json.dumps(evidence_refs)
        except (TypeError, ValueError) as exc:
            raise ValueError("evidence_refs must be JSON-serializable") from exc
    
    # Get current owner for entity
    current_owner = get_current_owner(entity_ref)
    
    # DS-2 enforcement: Refuse if no current owner
    if current_owner is None:
        raise ValueError(
            f"Constitutional refusal (DS-2: Unowned Recognition): "
            f"Entity '{entity_ref}' has no current recognition owner. "
            f"Declarations require explicit ownership. "
            f"Call assign_owner() first."
        )
    
    # DS-2 enforcement: Refuse if actor is not the current owner
    if current_owner != actor_ref:
        raise ValueError(
            f"Constitutional refusal (DS-2: No Proxy Recognition): "
            f"Actor '{actor_ref}' is not the current recognition owner for '{entity_ref}'. "
            f"Current owner: '{current_owner}'. "
            f"No proxy recognition allowed. Only the assigned owner can declare state."
        )
    
    # All validations passed - write to State Ledger
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO state__declarations
            (entity_ref, scope_ref, state_text,
             declared_by_actor_ref, declaration_kind, supersedes_declaration_id, cutter_evidence_ref, evidence_refs_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (entity_ref, scope_ref, state_text,
              actor_ref, declaration_kind, supersedes_declaration_id, cutter_evidence_ref, evidence_refs_json))
        
        declaration_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return declaration_id
        
    except sqlite3.IntegrityError as e:
        conn.close()
        raise ValueError(f"Failed to emit state declaration: {e}")


def get_declarations(
    entity_ref: Optional[str] = None,
    scope_ref: Optional[str] = None,
    actor_ref: Optional[str] = None,
    limit: Optional[int] = None
) -> list:
    """
    Query state declarations (read-only access to State Ledger).
    
    Args:
        entity_ref: Filter by entity (optional)
        scope_ref: Filter by scope (optional)
        actor_ref: Filter by declaring actor (optional)
        limit: Maximum number of results (optional)
    
    Returns:
        List of declaration dicts
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT
            declaration_id, entity_ref, scope_ref, state_text,
            classification, declaration_kind, declared_by_actor_ref, declared_at,
            supersedes_declaration_id, cutter_evidence_ref, evidence_refs_json
        FROM state__declarations
    """
    
    conditions = []
    params = []
    
    if entity_ref:
        conditions.append("entity_ref = ?")
        params.append(entity_ref)
    
    if scope_ref:
        conditions.append("scope_ref = ?")
        params.append(scope_ref)
    
    if actor_ref:
        conditions.append("declared_by_actor_ref = ?")
        params.append(actor_ref)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY declared_at DESC"
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    
    declarations = []
    for row in cursor.fetchall():
        declarations.append({
            'declaration_id': row['declaration_id'],
            'entity_ref': row['entity_ref'],
            'scope_ref': row['scope_ref'],
            'state_text': row['state_text'],
            'classification': row['classification'],
            'declaration_kind': row['declaration_kind'],
            'declared_by_actor_ref': row['declared_by_actor_ref'],
            'declared_at': row['declared_at'],
            'supersedes_declaration_id': row['supersedes_declaration_id'],
            'cutter_evidence_ref': row['cutter_evidence_ref'],
            'evidence_refs_json': row['evidence_refs_json']
        })
    
    conn.close()
    return declarations


def query_unowned_entities() -> list:
    """
    Query DS-2: Unowned Recognition.
    
    Returns entities with no current recognition owner.
    
    Constitutional Note:
    - This is structural visibility, not an alert
    - No inference or recommendation provided
    - No scoring or prioritization applied
    - Returns raw data for human judgment
    
    Returns:
        List of unowned entity dicts
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM view_ds2_unowned_recognition")
    
    entities = []
    for row in cursor.fetchall():
        entities.append({
            'entity_ref': row['entity_ref'],
            'entity_label': row['entity_label'],
            'cadence_days': row['cadence_days'],
            'entity_created_at': row['entity_created_at']
        })
    
    conn.close()
    return entities


def query_deferred_recognition() -> list:
    """
    Query DS-5: Deferred Recognition.
    
    Returns entities past their cadence window (no recent declaration).
    
    Constitutional Note:
    - This is structural visibility, not an alert
    - No inference or recommendation provided
    - No scoring or prioritization applied
    - Returns raw data for human judgment
    - Makes silence queryable, not actionable
    
    Returns:
        List of deferred entity dicts
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM view_ds5_deferred_recognition")
    
    entities = []
    for row in cursor.fetchall():
        entities.append({
            'entity_ref': row['entity_ref'],
            'entity_label': row['entity_label'],
            'cadence_days': row['cadence_days'],
            'last_declaration_at': row['last_declaration_at'],
            'days_since_last_declaration': row['days_since_last_declaration']
        })
    
    conn.close()
    return entities
