"""
Query A read-only access helpers (Loop 1).
"""

from typing import Optional, Dict, Any, List
from pathlib import Path

import database
from state_ledger import queries as state_queries


def get_query_a_open_deadlines(
    db_path: Optional[Path] = None,
    entity_ref: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Read Query A results with optional exact-match entity_ref filter.
    """
    resolved_path = db_path
    if resolved_path is None:
        resolved_path = database.resolve_db_path()

    results = state_queries.query_open_deadlines(db_path=resolved_path)
    if entity_ref:
        results = [row for row in results if row.get('entity_ref') == entity_ref]
    return results
