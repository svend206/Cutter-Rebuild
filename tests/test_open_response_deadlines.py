"""
Test Query A2: Open response_by declarations with no response_received.
"""

import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cutter_ledger import queries as cutter_queries


class TestOpenResponseDeadlines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp_dir = tempfile.gettempdir()
        cls.test_db = Path(temp_dir) / "test_open_response_deadlines.db"
        os.environ["TEST_DB_PATH"] = str(cls.test_db)

    def setUp(self):
        import database
        database.require_test_db("open_response_deadlines test")

        if self.test_db.exists():
            self.test_db.unlink()

        result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode != 0:
            raise RuntimeError(f"reset_db failed: {result.stderr}")

    def test_open_response_deadlines_filters_by_event(self):
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO state__entities (entity_ref, entity_label, cadence_days)
            VALUES
            ('entity:aaa', 'Entity AAA', 7),
            ('entity:bbb', 'Entity BBB', 7)
        """)
        cursor.execute("""
            INSERT INTO state__declarations
            (entity_ref, scope_ref, state_text, declaration_kind, declared_by_actor_ref, declared_at)
            VALUES
            ('entity:aaa', 'promise:response_by', '{"deadline":"2026-02-01T00:00:00Z"}', 'RECLASSIFICATION', 'org:test/actor:a', '2026-01-01T00:00:00Z'),
            ('entity:bbb', 'promise:response_by', '{"deadline":"2026-02-02T00:00:00Z"}', 'RECLASSIFICATION', 'org:test/actor:b', '2026-01-02T00:00:00Z')
        """)
        conn.commit()
        conn.close()

        results = cutter_queries.query_open_response_deadlines(db_path=self.test_db)
        entity_refs = {row["entity_ref"] for row in results}
        self.assertIn("entity:aaa", entity_refs)
        self.assertIn("entity:bbb", entity_refs)

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cutter__events (event_type, subject_ref, event_data, created_at)
            VALUES ('response_received', 'entity:bbb', '{"source":"test"}', '2026-01-02T01:00:00Z')
        """)
        conn.commit()
        conn.close()

        results = cutter_queries.query_open_response_deadlines(db_path=self.test_db)
        entity_refs = {row["entity_ref"] for row in results}
        self.assertIn("entity:aaa", entity_refs)
        self.assertNotIn("entity:bbb", entity_refs)

    def test_malformed_state_text_raises(self):
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO state__entities (entity_ref, entity_label, cadence_days)
            VALUES ('entity:bad', 'Entity Bad', 7)
        """)
        cursor.execute("""
            INSERT INTO state__declarations
            (entity_ref, scope_ref, state_text, declaration_kind, declared_by_actor_ref, declared_at)
            VALUES
            ('entity:bad', 'promise:response_by', '{bad json}', 'RECLASSIFICATION', 'org:test/actor:z', '2026-01-01T00:00:00Z')
        """)
        conn.commit()
        conn.close()

        with self.assertRaises(ValueError):
            cutter_queries.query_open_response_deadlines(db_path=self.test_db)
