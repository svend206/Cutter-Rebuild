"""
Test Query B: Dwell time vs expectation.
"""

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cutter_ledger import queries as cutter_queries


class TestDwellVsExpectation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp_dir = tempfile.gettempdir()
        cls.test_db = Path(temp_dir) / "test_dwell_vs_expectation.db"
        os.environ["TEST_DB_PATH"] = str(cls.test_db)

    def setUp(self):
        import database
        database.require_test_db("dwell_vs_expectation test")

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

    def test_elapsed_and_delta(self):
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cutter__events (event_type, subject_ref, event_data, created_at)
            VALUES
            ('stage_started', 'entity:bbb', '{"stage":"machining"}', '2026-01-01T00:00:00Z'),
            ('stage_completed', 'entity:bbb', '{"stage":"machining"}', '2026-01-01T01:00:00Z'),
            ('stage_started', 'entity:bbb', '{"stage":"inspection"}', '2026-01-01T01:00:00Z')
        """)
        conn.commit()
        conn.close()

        results = cutter_queries.query_dwell_vs_expectation(
            db_path=self.test_db,
            now="2026-01-01T01:30:00Z"
        )

        by_stage = {row["stage"]: row for row in results}
        machining = by_stage["machining"]
        inspection = by_stage["inspection"]

        self.assertEqual(machining["elapsed_seconds"], 3600)
        self.assertEqual(machining["expected_seconds"], 3600)
        self.assertEqual(machining["delta_seconds"], 0)

        self.assertEqual(inspection["elapsed_seconds"], 1800)
        self.assertEqual(inspection["expected_seconds"], 1800)
        self.assertEqual(inspection["delta_seconds"], 0)

    def test_malformed_event_data_raises(self):
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cutter__events (event_type, subject_ref, event_data, created_at)
            VALUES ('stage_started', 'entity:bad', '{bad json}', '2026-01-01T00:00:00Z')
        """)
        conn.commit()
        conn.close()

        with self.assertRaises(ValueError):
            cutter_queries.query_dwell_vs_expectation(
                db_path=self.test_db,
                now="2026-01-01T01:00:00Z"
            )
