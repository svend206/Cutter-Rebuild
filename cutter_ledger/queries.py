"""
Cutter Ledger Query Functions (Read-Only)
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

import database
from ops_layer.stage_expectations import get_expected_duration_seconds


def _parse_iso_ts(value: str) -> datetime:
    if value.endswith("Z"):
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        dt = datetime.fromisoformat(value)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def query_dwell_vs_expectation(
    db_path: Optional[Path] = None,
    subject_ref: Optional[str] = None,
    now: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None
) -> List[Dict[str, Any]]:
    """
    Query dwell time vs expectation for stage events.
    """
    owns_conn = False
    if conn is None:
        if db_path is not None:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            owns_conn = True
        else:
            resolved = database.resolve_db_path()
            conn = sqlite3.connect(resolved)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            owns_conn = True
    cursor = conn.cursor()

    params: List[Any] = []
    subject_clause = ""
    if subject_ref is not None:
        subject_clause = "AND subject_ref = ?"
        params.append(subject_ref)

    cursor.execute(f"""
        SELECT event_type, subject_ref, event_data, created_at
        FROM cutter__events
        WHERE event_type IN ('stage_started', 'stage_completed')
        {subject_clause}
        ORDER BY created_at ASC
    """, params)

    events: Dict[str, Dict[str, Dict[str, Optional[str]]]] = {}
    for row in cursor.fetchall():
        if row["event_data"] is None:
            if owns_conn:
                conn.close()
            raise ValueError(f"Missing event_data for {row['subject_ref']}")
        try:
            payload = json.loads(row["event_data"])
        except json.JSONDecodeError as exc:
            if owns_conn:
                conn.close()
            raise ValueError(f"Malformed event_data JSON for {row['subject_ref']}: {exc}") from exc

        if not isinstance(payload, dict) or "stage" not in payload:
            if owns_conn:
                conn.close()
            raise ValueError(f"Missing stage in event_data for {row['subject_ref']}")

        stage = payload["stage"]
        subject = row["subject_ref"]
        event_type = row["event_type"]
        created_at = row["created_at"]

        if subject not in events:
            events[subject] = {}
        if stage not in events[subject]:
            events[subject][stage] = {"started_at": None, "completed_at": None}

        if event_type == "stage_started" and events[subject][stage]["started_at"] is None:
            events[subject][stage]["started_at"] = created_at
        if event_type == "stage_completed" and events[subject][stage]["completed_at"] is None:
            events[subject][stage]["completed_at"] = created_at

    results: List[Dict[str, Any]] = []
    now_dt = _parse_iso_ts(now) if now is not None else datetime.utcnow()

    for subject, stages in events.items():
        for stage, timestamps in stages.items():
            started_at = timestamps["started_at"]
            completed_at = timestamps["completed_at"]

            if started_at is None:
                continue

            started_dt = _parse_iso_ts(started_at)
            if completed_at is not None:
                completed_dt = _parse_iso_ts(completed_at)
                elapsed_seconds = int((completed_dt - started_dt).total_seconds())
            else:
                elapsed_seconds = int((now_dt - started_dt).total_seconds())

            expected_seconds = get_expected_duration_seconds(stage)
            delta_seconds = elapsed_seconds - expected_seconds

            results.append({
                "subject_ref": subject,
                "stage": stage,
                "started_at": started_at,
                "completed_at": completed_at,
                "elapsed_seconds": elapsed_seconds,
                "expected_seconds": expected_seconds,
                "delta_seconds": delta_seconds
            })

    if owns_conn:
        conn.close()
    return results


def query_open_response_deadlines(
    db_path: Optional[Path] = None,
    entity_ref: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None
) -> List[Dict[str, Any]]:
    """
    Query promise:response_by declarations with no response_received event.
    """
    owns_conn = False
    if conn is None:
        if db_path is not None:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            owns_conn = True
        else:
            resolved = database.resolve_db_path()
            conn = sqlite3.connect(resolved)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            owns_conn = True
    cursor = conn.cursor()

    params: List[Any] = []
    entity_clause = ""
    if entity_ref is not None:
        entity_clause = "AND d.entity_ref = ?"
        params.append(entity_ref)

    cursor.execute(f"""
        SELECT d.entity_ref, d.state_text, d.declared_at, d.declared_by_actor_ref
        FROM state__declarations d
        WHERE d.scope_ref = 'promise:response_by'
        {entity_clause}
        AND NOT EXISTS (
            SELECT 1
            FROM cutter__events e
            WHERE e.event_type = 'response_received'
            AND e.subject_ref = d.entity_ref
        )
        ORDER BY d.declared_at ASC
    """, params)

    results: List[Dict[str, Any]] = []
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
