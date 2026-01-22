import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

# Ensure isolated DB before importing app/database
TEST_DB_PATH = Path(tempfile.gettempdir()) / "test_mvp12_reconciliation.db"
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
        body = response.get_json()
        self.assertTrue(body.get("success"))
        reconciliation = body.get("reconciliation", {})
        self.assertEqual(reconciliation.get("scope_ref"), payload["scope_ref"])
        self.assertEqual(reconciliation.get("scope_kind"), payload["scope_kind"])
        self.assertEqual(reconciliation.get("predicate_ref"), payload["predicate_ref"])
        self.assertEqual(reconciliation.get("predicate_text"), payload["predicate_text"])
        self.assertEqual(reconciliation.get("actor_ref"), payload["actor_ref"])

        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ops__reconciliations")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)

    def test_reconciliation_allows_missing_predicate_text(self) -> None:
        payload = {
            "scope_ref": "org:acme/scope:weekly-review",
            "scope_kind": "report",
            "predicate_ref": "scope=weekly-review/report=ops-unclosed-quotes",
            "actor_ref": "org:acme/actor:auditor"
        }
        response = self.client.post(
            "/api/reconcile",
            headers={"X-Ops-Mode": "planning"},
            json=payload
        )
        self.assertEqual(response.status_code, 200)
        reconciliation = response.get_json().get("reconciliation", {})
        self.assertEqual(reconciliation.get("predicate_ref"), payload["predicate_ref"])
        self.assertIsNone(reconciliation.get("predicate_text"))

        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT predicate_text
            FROM ops__reconciliations
            WHERE predicate_ref = ?
        """, (payload["predicate_ref"],))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertIsNone(row[0])

    def test_reconciliation_binding_ignores_predicate_text_variance(self) -> None:
        predicate_ref = "scope=weekly-review/report=ops-unclosed-quotes"
        payload_one = {
            "scope_ref": "org:acme/scope:weekly-review",
            "scope_kind": "report",
            "predicate_ref": predicate_ref,
            "predicate_text": "scope=weekly-review; report=ops-unclosed-quotes",
            "actor_ref": "org:acme/actor:auditor"
        }
        payload_two = {
            "scope_ref": "org:acme/scope:weekly-review",
            "scope_kind": "report",
            "predicate_ref": predicate_ref,
            "predicate_text": "scope=weekly-review; report=ops-unclosed-quotes; v2",
            "actor_ref": "org:acme/actor:auditor"
        }
        for payload in (payload_one, payload_two):
            response = self.client.post(
                "/api/reconcile",
                headers={"X-Ops-Mode": "planning"},
                json=payload
            )
            self.assertEqual(response.status_code, 200)

        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT predicate_ref, predicate_text
            FROM ops__reconciliations
            WHERE predicate_ref = ?
        """, (predicate_ref,))
        rows = cursor.fetchall()
        conn.close()
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row[0] == predicate_ref for row in rows))


if __name__ == "__main__":
    unittest.main()
