import os
import sqlite3
import unittest
from pathlib import Path

# Ensure isolated DB before importing app/database
TEST_DB_PATH = Path(__file__).parent / "test_mvp13_execution_continuity.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

from scripts import reset_db

reset_db.create_fresh_db(TEST_DB_PATH)

from ops_layer import app as app_module


class TestMVP13ExecutionContinuity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = app_module.app.test_client()

    def setUp(self) -> None:
        os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)
        reset_db.create_fresh_db(TEST_DB_PATH)

    def _count_cutter_events(self) -> int:
        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cutter__events")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def _count_reconciliations(self) -> int:
        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ops__reconciliations")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def _save_quote(self, headers: dict | None = None):
        payload = {
            "shape_config": {
                "type": "block",
                "dimensions": {"x": 2.0, "y": 1.0, "z": 1.0},
                "volume": 2.0
            },
            "material": "Aluminum 6061",
            "quantity": 1,
            "system_price_anchor": 10.0,
            "final_quoted_price": 10.0,
            "customer_name": "Test Customer",
            "contact_name": "Test Contact",
            "contact_email": "test@example.com"
        }
        return self.client.post("/save_quote", json=payload, headers=headers or {})

    def test_execution_continues_with_reconciliation_present(self) -> None:
        payload = {
            "scope_ref": "org:acme/scope:weekly-review",
            "scope_kind": "report",
            "predicate_ref": "scope=weekly-review/report=ops-unclosed-quotes",
            "predicate_text": "scope=weekly-review; report=ops-unclosed-quotes",
            "actor_ref": "org:acme/actor:auditor"
        }
        response = self.client.post(
            "/api/reconcile",
            headers={"X-Ops-Mode": "planning"},
            json=payload
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._count_reconciliations(), 1)

        before_events = self._count_cutter_events()
        quote_response = self._save_quote()
        self.assertEqual(quote_response.status_code, 200)
        body = quote_response.get_json()
        self.assertTrue(body.get("success"))
        self.assertGreater(self._count_cutter_events(), before_events)

    def test_execution_continues_without_reconciliation(self) -> None:
        self.assertEqual(self._count_reconciliations(), 0)
        before_events = self._count_cutter_events()
        quote_response = self._save_quote()
        self.assertEqual(quote_response.status_code, 200)
        body = quote_response.get_json()
        self.assertTrue(body.get("success"))
        self.assertGreater(self._count_cutter_events(), before_events)

    def test_execution_continues_during_planning_activity(self) -> None:
        payload = {
            "scope_ref": "org:acme/scope:monthly-review",
            "scope_kind": "query",
            "predicate_ref": "scope=monthly-review/query=ops-quote-flow",
            "predicate_text": "scope=monthly-review; query=ops-quote-flow",
            "actor_ref": "org:acme/actor:planner"
        }
        response = self.client.post(
            "/api/reconcile",
            headers={"X-Ops-Mode": "planning"},
            json=payload
        )
        self.assertEqual(response.status_code, 200)

        before_events = self._count_cutter_events()
        quote_response = self._save_quote(headers={"X-Ops-Mode": "planning"})
        self.assertEqual(quote_response.status_code, 200)
        body = quote_response.get_json()
        self.assertTrue(body.get("success"))
        self.assertGreater(self._count_cutter_events(), before_events)


if __name__ == "__main__":
    unittest.main()
