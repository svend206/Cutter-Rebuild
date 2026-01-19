"""
Test Query A: Open promise:deadline declarations.
"""

import os
import sqlite3
import tempfile
import time
import unittest
import json
import subprocess
import sys
from pathlib import Path


class TestOpenDeadlineQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time() * 1000)
        cls.test_db = Path(temp_dir) / f"test_open_deadlines_{timestamp}.db"
        os.environ["TEST_DB_PATH"] = str(cls.test_db)

    def setUp(self):
        import database
        database.require_test_db("open_deadline_query test")

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

        import importlib
        from state_ledger import queries as state_queries
        importlib.reload(state_queries)

    def test_open_deadlines_filters_by_scope_and_handoff(self):
        from state_ledger import queries as state_queries

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO state__entities (entity_ref, entity_label, cadence_days)
            VALUES
            ('entity:aaa', 'Entity AAA', 7),
            ('entity:bbb', 'Entity BBB', 7),
            ('entity:ccc', 'Entity CCC', 7)
        """)
        cursor.execute("""
            INSERT INTO state__declarations
            (entity_ref, scope_ref, state_text, declaration_kind, declared_by_actor_ref, declared_at)
            VALUES
            ('entity:aaa', 'promise:deadline', '{"deadline":"2026-02-01T00:00:00Z"}', 'RECLASSIFICATION', 'org:test/actor:a', '2026-01-01T00:00:00Z'),
            ('entity:bbb', 'promise:deadline', '{"deadline":"2026-02-02T00:00:00Z"}', 'RECLASSIFICATION', 'org:test/actor:b', '2026-01-02T00:00:00Z'),
            ('entity:ccc', 'promise:other', '{"deadline":"2026-02-03T00:00:00Z"}', 'RECLASSIFICATION', 'org:test/actor:c', '2026-01-03T00:00:00Z')
        """)
        conn.commit()
        conn.close()

        results = state_queries.query_open_deadlines(db_path=self.test_db)
        entity_refs = {row["entity_ref"] for row in results}
        self.assertIn("entity:bbb", entity_refs)

        from ops_layer.query_a import get_query_a_open_deadlines
        query_a_results = get_query_a_open_deadlines(db_path=self.test_db)
        self.assertEqual(query_a_results, results)

        filtered_results = get_query_a_open_deadlines(db_path=self.test_db, entity_ref="entity:bbb")
        self.assertTrue(all(row["entity_ref"] == "entity:bbb" for row in filtered_results))

        from ops_layer.ledger_events import emit_carrier_handoff
        emit_carrier_handoff(subject_ref='entity:bbb', carrier='UPS')

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_type, subject_ref, event_data
            FROM cutter__events
            WHERE subject_ref = 'entity:bbb'
        """)
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'carrier_handoff')
        self.assertEqual(row[1], 'entity:bbb')
        payload = json.loads(row[2]) if row[2] else {}
        self.assertEqual(payload.get('carrier'), 'UPS')

        results = state_queries.query_open_deadlines(db_path=self.test_db)
        entity_refs = {row["entity_ref"] for row in results}
        self.assertNotIn("entity:bbb", entity_refs)

    def test_malformed_state_text_raises(self):
        from state_ledger import queries as state_queries

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
            ('entity:bad', 'promise:deadline', '{bad json}', 'RECLASSIFICATION', 'org:test/actor:z', '2026-01-01T00:00:00Z')
        """)
        conn.commit()
        conn.close()

        with self.assertRaises(ValueError):
            state_queries.query_open_deadlines(db_path=self.test_db)
