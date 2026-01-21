import os
import sqlite3
import unittest
from pathlib import Path

# Ensure isolated DB before importing app/database
TEST_DB_PATH = Path(__file__).parent / "test_mvp12_reconciliation.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

from scripts import reset_db

reset_db.create_fresh_db(TEST_DB_PATH)

from ops_layer import app as app_module


class TestMVP12Reconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = app_module.app.test_client()

    def setUp(self) -> None:
        os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)
        reset_db.create_fresh_db(TEST_DB_PATH)

    def test_reconciliation_records_query_scoped_entry(self) -> None:
        os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)
        payload = {
            "scope_ref": "org:acme/scope:weekly-review",
            "scope_kind": "report",
            "predicate_text": "scope=weekly-review; report=ops-unclosed-quotes",
            "actor_ref": "org:acme/actor:auditor"
        }
        response = self.client.post(
            "/api/reconcile",
            headers={"X-Ops-Mode": "planning"},
            json=payload
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body.get("success"))
        reconciliation = body.get("reconciliation", {})
        self.assertEqual(reconciliation.get("scope_ref"), payload["scope_ref"])
        self.assertEqual(reconciliation.get("scope_kind"), payload["scope_kind"])
        self.assertEqual(reconciliation.get("predicate_text"), payload["predicate_text"])
        self.assertEqual(reconciliation.get("actor_ref"), payload["actor_ref"])

        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ops__reconciliations")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
