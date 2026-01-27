import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

# Ensure isolated DB before importing app/database
TEST_DB_PATH = Path(tempfile.gettempdir()) / "test_trace_vi_op_04.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

from scripts import reset_db

reset_db.create_fresh_db(TEST_DB_PATH)

from ops_layer import app as app_module


class TraceVIOp04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = app_module.app.test_client()
        cls.ops_headers = {"X-Ops-Mode": "planning"}

    def setUp(self) -> None:
        os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)
        reset_db.create_fresh_db(TEST_DB_PATH)

    def _fetch_refusal_events(self, query_ref: str):
        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_type
            FROM cutter__events
            WHERE subject_ref = ?
            ORDER BY id ASC
        """, (f"query:{query_ref}",))
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def test_refusal_is_not_softened_or_partial(self) -> None:
        payloads = [
            {
                "query_ref": "blame.operator-score",
                "query_text": "score operators by overrides",
                "actor_ref": "org:acme/actor:auditor"
            },
            {
                "query_ref": "blame.operator-unknown",
                "query_text": "score operators by unknown metric",
                "actor_ref": "org:acme/actor:auditor"
            }
        ]
        for payload in payloads:
            response = self.client.post("/api/query/refusal", json=payload, headers=self.ops_headers)
            self.assertEqual(response.status_code, 403)
            body = response.get_json() or {}
            self.assertIs(body.get("refused"), True)
            self.assertIs(body.get("success"), False)
            self.assertEqual(set(body.keys()), {"success", "refused", "refusal", "event_id"})
            refusal = body.get("refusal", {})
            self.assertIsInstance(refusal.get("category"), str)
            self.assertNotEqual(refusal.get("category", "").strip(), "")
            self.assertIsInstance(refusal.get("reason"), str)
            self.assertNotEqual(refusal.get("reason", "").strip(), "")
            self.assertEqual(
                self._fetch_refusal_events(payload["query_ref"]),
                ["REFUSAL_EMITTED"]
            )


if __name__ == "__main__":
    unittest.main()
