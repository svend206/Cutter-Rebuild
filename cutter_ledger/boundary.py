"""
Cutter Ledger Boundary - Single Authorized Write Path

This module is the ONLY location permitted to INSERT into cutter__events.
All operational exhaust from the Ops layer must pass through emit_cutter_event().

Constitutional Enforcement:
- C1 (Outcome Agnosticism): Event types must be descriptive, never evaluative
- C2 (Outcome Agnosticism): Industry-agnostic storage (subject_ref, no domain coupling)
- C4 (Irreversible Memory): Events cannot be edited or deleted (enforced by DB triggers)
- C7 (Overrides Must Leave Scars): Override events preserve magnitude, frequency, persistence

CRITICAL: No other module should write to cutter__events directly.
"""

import sqlite3
import json
import inspect
import subprocess
import os
from pathlib import Path
from typing import Optional, Dict, Any


# Support TEST_DB_PATH for hermetic testing
def _get_db_path() -> Path:
    """Get database path (respects TEST_DB_PATH environment variable)."""
    test_db_path = os.environ.get('TEST_DB_PATH')
    if test_db_path:
        return Path(test_db_path)
    return Path("cutter.db")


DB_PATH = _get_db_path()

# Deterministic provenance constants
SERVICE_ID = "cutter_ops_v1"  # Service/app identifier (industry-agnostic)


def get_version() -> str:
    """Get current git SHA (deterministic version identifier)."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def get_connection() -> sqlite3.Connection:
    """
    Get database connection with WAL mode (Constitutional requirement C2).
    Respects TEST_DB_PATH environment variable for hermetic testing.
    """
    db_path = _get_db_path()  # Re-evaluate in case TEST_DB_PATH changed
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")  # CRITICAL: Constitution Rule #2
    return conn


def emit_cutter_event(
    event_type: str,
    subject_ref: Optional[str] = None,
    event_data: Optional[Dict[str, Any]] = None,
    service_id: Optional[str] = None,
    version: Optional[str] = None
) -> int:
    """
    Emit an operational event to the Cutter Ledger (append-only).
    
    This is the ONLY authorized write path into cutter__events.
    
    CONSTITUTIONAL CONSTRAINTS:
    - C1 (Outcome Agnosticism): Event types must be descriptive, never evaluative
    - C2 (Outcome Agnosticism): Industry-agnostic storage (subject_ref TEXT, no domain coupling)
    - C4 (Irreversible Memory): Events cannot be edited or deleted (enforced by DB triggers)
    - C7 (Overrides Must Leave Scars): Override events preserve magnitude, frequency, persistence
    
    PROVENANCE DESIGN:
    - Deterministic: service_id and version are constant per deployment
    - No stack inspection: Provenance based on service identity, not caller
    - Debug callsite: Optionally captured in event_data.debug.callsite (best-effort)
    
    Args:
        event_type: Descriptive event name (e.g., "ENTITY_OVERRIDDEN", "WORKFLOW_STARTED")
                   Must NOT contain evaluative language (good/bad/healthy/risky)
        subject_ref: Subject reference string (e.g., "quote:123", "job:456", "unknown")
                    Industry-agnostic identifier (no FK coupling)
        event_data: JSON-serializable dict with event-specific data
        service_id: Service/app identifier (defaults to SERVICE_ID constant)
        version: Git SHA or version (defaults to current git HEAD)
    
    Returns:
        Event record ID (integer)
    
    Raises:
        ValueError: If event_type contains evaluative language
    """
    # C1: Refuse evaluative event types (Constitutional enforcement)
    forbidden_words = [
        'good', 'bad', 'healthy', 'unhealthy', 'risky', 'safe', 
        'problem', 'issue', 'warning', 'error', 'concern'
    ]
    event_type_lower = event_type.lower()
    for word in forbidden_words:
        if word in event_type_lower:
            raise ValueError(
                f"Event type '{event_type}' contains evaluative language ('{word}'). "
                f"Use descriptive vocabulary only."
            )
    
    # Deterministic provenance
    ingested_by_service = service_id or SERVICE_ID
    ingested_by_version = version or get_version()
    
    # Optional: Best-effort callsite capture (debug metadata only)
    if event_data is None:
        event_data = {}
    
    if 'debug' not in event_data:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_frame = frame.f_back
            module_name = caller_frame.f_globals.get('__name__', 'unknown')
            function_name = caller_frame.f_code.co_name
            event_data['debug'] = {
                'callsite': f"{module_name}.{function_name}"
            }
    
    # Normalize subject_ref to string (industry-agnostic)
    if subject_ref is None:
        subject_ref_str = "unknown"
    elif isinstance(subject_ref, int):
        # Legacy compatibility: convert int to "quote:{id}" format
        subject_ref_str = f"quote:{subject_ref}"
    else:
        subject_ref_str = str(subject_ref)
    
    # Serialize event data
    event_data_json = json.dumps(event_data) if event_data else None
    
    # INSERT into Cutter Ledger (ONLY authorized write location)
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO cutter__events 
        (event_type, subject_ref, event_data, ingested_by_service, ingested_by_version)
        VALUES (?, ?, ?, ?, ?)
    """, (event_type, subject_ref_str, event_data_json, ingested_by_service, ingested_by_version))
    
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return event_id


def get_events(subject_ref: Optional[str] = None, event_type: Optional[str] = None) -> list:
    """
    Read events from the Cutter Ledger (industry-agnostic, read-only access).
    
    Args:
        subject_ref: Filter by subject reference string (e.g., "quote:123") (optional, returns all if None)
        event_type: Filter by event type (optional)
    
    Returns:
        List of event dicts with id, event_type, subject_ref, event_data, created_at, 
        ingested_by_service, ingested_by_version
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build query dynamically based on filters
    query = """
        SELECT id, event_type, subject_ref, event_data, created_at, 
               ingested_by_service, ingested_by_version
        FROM cutter__events
    """
    params = []
    conditions = []
    
    if subject_ref is not None:
        # Normalize subject_ref for query (handle int for backward compatibility)
        if isinstance(subject_ref, int):
            subject_ref_str = f"quote:{subject_ref}"
        else:
            subject_ref_str = str(subject_ref)
        conditions.append("subject_ref = ?")
        params.append(subject_ref_str)
    
    if event_type is not None:
        conditions.append("event_type = ?")
        params.append(event_type)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at ASC"
    
    cursor.execute(query, params)
    
    events = []
    for row in cursor.fetchall():
        events.append({
            'id': row['id'],
            'event_type': row['event_type'],
            'subject_ref': row['subject_ref'],  # Already industry-agnostic
            'event_data': json.loads(row['event_data']) if row['event_data'] else None,
            'created_at': row['created_at'],
            'ingested_by_service': row['ingested_by_service'],
            'ingested_by_version': row['ingested_by_version']
        })
    
    conn.close()
    return events


# Backward compatibility wrapper (deprecated)
def get_events_for_quote(quote_id: int) -> list:
    """
    DEPRECATED: Use get_events(subject_ref="quote:{id}") instead.
    
    Maintained for backward compatibility only.
    Converts quote_id (int) to subject_ref format ("quote:{id}").
    """
    # Convert int quote_id to subject_ref string format
    subject_ref_str = f"quote:{quote_id}"
    return get_events(subject_ref=subject_ref_str)
