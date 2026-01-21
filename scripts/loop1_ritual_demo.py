#!/usr/bin/env python3
"""
Loop 1 cadence ritual demo (read-only surfaces, raw rows only).
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from state_ledger import queries as state_queries
from ops_layer.ledger_events import emit_carrier_handoff


def reset_demo_db(db_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, 'scripts/reset_db.py', '--db-path', str(db_path)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    if result.returncode != 0:
        raise RuntimeError(f"reset_db failed: {result.stderr}")


def seed_demo_state(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO state__entities (entity_ref, entity_label, cadence_days)
        VALUES ('entity:demo', 'Entity Demo', 7)
    """)
    cursor.execute("""
        INSERT INTO state__declarations
        (entity_ref, scope_ref, state_text, declaration_kind, declared_by_actor_ref, declared_at)
        VALUES
        ('entity:demo', 'promise:deadline', '{"deadline":"2026-02-01T00:00:00Z"}',
         'RECLASSIFICATION', 'org:demo/actor:system', '2026-01-01T00:00:00Z')
    """)
    conn.commit()
    conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Loop 1 cadence ritual demo")
    parser.add_argument("--db-path", help="Path to demo database")
    args = parser.parse_args()

    if args.db_path:
        db_path = Path(args.db_path)
    else:
        temp_dir = tempfile.gettempdir()
        db_path = Path(temp_dir) / "test_loop1_ritual_demo.db"

    os.environ["TEST_DB_PATH"] = str(db_path)
    import contextlib
    with contextlib.redirect_stdout(sys.stderr):
        import database
        import importlib
        importlib.reload(database)
    database.require_test_db("loop1_ritual_demo")

    reset_demo_db(db_path)
    seed_demo_state(db_path)

    results_before = state_queries.query_open_deadlines(db_path=db_path)
    print(json.dumps(results_before, default=str))

    emit_carrier_handoff(subject_ref="entity:demo")

    results_after = state_queries.query_open_deadlines(db_path=db_path)
    print(json.dumps(results_after, default=str))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
