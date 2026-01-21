import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from state_ledger.boundary import register_entity, assign_owner
import database


class TestStateTimeInState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.test_db_path = Path(cls.test_dir) / "test_state_time_in_state.db"
        os.environ["TEST_DB_PATH"] = str(cls.test_db_path)
        database.require_test_db("time-in-state tests")

        result = subprocess.run(
            [sys.executable, "scripts/reset_db.py", "--db-path", str(cls.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode != 0:
            raise RuntimeError(f"reset_db failed: {result.stderr}")

    @classmethod
    def tearDownClass(cls):
        if cls.test_db_path.exists():
            cls.test_db_path.unlink()
        for suffix in ("-wal", "-shm"):
            extra = Path(str(cls.test_db_path) + suffix)
            if extra.exists():
                extra.unlink()

    def test_time_in_state_returns_latest_declaration(self):
        os.environ["TEST_DB_PATH"] = str(self.test_db_path)
        entity_ref = "org:acme/entity:project:alpha"
        scope_ref = "org:acme/scope:weekly"
        actor_ref = "org:acme/actor:owner"

        register_entity(entity_ref, "Acme Alpha", cadence_days=7)
        assign_owner(entity_ref, actor_ref, "org:acme/actor:admin")

        now = datetime.now(timezone.utc)
        older = (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        newer = (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(str(self.test_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO state__declarations
            (entity_ref, scope_ref, state_text, declaration_kind, declared_by_actor_ref, declared_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (entity_ref, scope_ref, "Initial state", "RECLASSIFICATION", actor_ref, older))
        cursor.execute("""
            INSERT INTO state__declarations
            (entity_ref, scope_ref, state_text, declaration_kind, declared_by_actor_ref, declared_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (entity_ref, scope_ref, "Reaffirmed state", "REAFFIRMATION", actor_ref, newer))
        conn.commit()
        conn.close()

        from state_ledger import queries as state_queries
        rows = state_queries.query_time_in_state()
        match = [row for row in rows if row["entity_ref"] == entity_ref and row["scope_ref"] == scope_ref]
        self.assertEqual(len(match), 1)
        latest = match[0]
        self.assertEqual(latest["declaration_kind"], "REAFFIRMATION")
        self.assertGreaterEqual(latest["days_since_declaration"], 1)


if __name__ == "__main__":
    unittest.main()
