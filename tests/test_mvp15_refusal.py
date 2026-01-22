import json
import os
import sqlite3
import unittest
from pathlib import Path

# Ensure isolated DB before importing app/database
TEST_DB_PATH = Path(__file__).parent / "test_mvp15_refusal.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

from scripts import reset_db

reset_db.create_fresh_db(TEST_DB_PATH)

from ops_layer import app as app_module


class TestMVP15Refusal(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = app_module.app.test_client()

    def setUp(self) -> None:
        os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)
        reset_db.create_fresh_db(TEST_DB_PATH)

    def _fetch_refusal_events(self, query_ref: str):
        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_data
            FROM cutter__events
            WHERE event_type = 'REFUSAL_EMITTED'
              AND subject_ref = ?
            ORDER BY id ASC
        """, (f"query:{query_ref}",))
        rows = cursor.fetchall()
        conn.close()
        return [json.loads(row[0]) for row in rows]

    def test_refuses_prohibited_query(self) -> None:
        payload = {
            "query_ref": "blame.operator-score",
            "query_text": "score operators by overrides",
            "actor_ref": "org:acme/actor:auditor"
        }
        response = self.client.post("/api/query/refusal", json=payload)
        self.assertEqual(response.status_code, 403)
        body = response.get_json()
        self.assertTrue(body.get("refused"))
        refusal = body.get("refusal", {})
        self.assertEqual(refusal.get("category"), "automated_harm_blame_computation")
        self.assertEqual(refusal.get("query_ref"), payload["query_ref"])
        self.assertEqual(refusal.get("query_class"), "refuse_blame")

        events = self._fetch_refusal_events(payload["query_ref"])
        self.assertEqual(len(events), 1)
        event_data = events[0]
        self.assertEqual(event_data.get("query_ref"), payload["query_ref"])
        self.assertEqual(event_data.get("actor_ref"), payload["actor_ref"])
        self.assertEqual(event_data.get("query_class"), "refuse_blame")
        self.assertEqual(event_data.get("query_text"), payload["query_text"])

    def test_refusal_not_bypassed_by_phrasing(self) -> None:
        query_ref = "blame.operator-score"
        payloads = [
            {
                "query_ref": query_ref,
                "query_text": "rank operators by override delta",
                "actor_ref": "org:acme/actor:auditor"
            },
            {
                "query_ref": query_ref,
                "query_text": "list worst operators by performance",
                "actor_ref": "org:acme/actor:auditor"
            }
        ]
        for payload in payloads:
            response = self.client.post("/api/query/refusal", json=payload)
            self.assertEqual(response.status_code, 403)

        events = self._fetch_refusal_events(query_ref)
        self.assertEqual(len(events), 2)
        self.assertTrue(all(event.get("query_ref") == query_ref for event in events))

    def test_refuses_new_query_ref_classified_as_blame(self) -> None:
        payload = {
            "query_ref": "blame.operator-latency-score",
            "query_text": "score operators by late deliveries",
            "actor_ref": "org:acme/actor:auditor"
        }
        response = self.client.post("/api/query/refusal", json=payload)
        self.assertEqual(response.status_code, 403)
        refusal = response.get_json().get("refusal", {})
        self.assertEqual(refusal.get("query_class"), "refuse_blame")

        events = self._fetch_refusal_events(payload["query_ref"])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].get("query_class"), "refuse_blame")

    def test_refuses_unclassified_query_ref(self) -> None:
        payload = {
            "query_ref": "blame.operator-unknown",
            "query_text": "score operators by unknown metric",
            "actor_ref": "org:acme/actor:auditor"
        }
        response = self.client.post("/api/query/refusal", json=payload)
        self.assertEqual(response.status_code, 403)
        refusal = response.get_json().get("refusal", {})
        self.assertEqual(refusal.get("category"), "unknown_query_class")
        self.assertEqual(refusal.get("query_class"), "unknown")

        events = self._fetch_refusal_events(payload["query_ref"])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].get("refusal_category"), "unknown_query_class")

    def test_allowed_queries_unaffected(self) -> None:
        response = self.client.get("/api/state/open-deadlines")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertIn("results", body)


if __name__ == "__main__":
    unittest.main()
