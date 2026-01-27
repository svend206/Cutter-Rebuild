import os
import tempfile
import unittest
from pathlib import Path

# Ensure isolated DB before importing app/database
TEST_DB_PATH = Path(tempfile.gettempdir()) / "test_trace_vi_op_03.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

from scripts import reset_db

reset_db.create_fresh_db(TEST_DB_PATH)

from ops_layer import app as app_module


class TraceVIOp03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = app_module.app.test_client()
        cls.ops_headers = {"X-Ops-Mode": "planning"}

    def setUp(self) -> None:
        os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)
        reset_db.create_fresh_db(TEST_DB_PATH)

    def test_refusal_is_explicit_and_visible(self) -> None:
        payload = {
            "query_ref": "blame.operator-score",
            "query_text": "score operators by overrides",
            "actor_ref": "org:acme/actor:auditor"
        }
        response = self.client.post("/api/query/refusal", json=payload, headers=self.ops_headers)
        self.assertEqual(response.status_code, 403)
        body = response.get_json() or {}

        self.assertIs(body.get("refused"), True)
        refusal = body.get("refusal", {})
        self.assertEqual(refusal.get("query_ref"), payload["query_ref"])
        self.assertEqual(refusal.get("query_class"), "refuse_blame")
        self.assertIsInstance(refusal.get("category"), str)
        self.assertNotEqual(refusal.get("category", "").strip(), "")
        self.assertIsInstance(refusal.get("reason"), str)
        self.assertNotEqual(refusal.get("reason", "").strip(), "")


if __name__ == "__main__":
    unittest.main()
