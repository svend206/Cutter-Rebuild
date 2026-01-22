import os
import tempfile
import unittest
from pathlib import Path

from scripts import reset_db

TEST_DB_PATH = Path(tempfile.gettempdir()) / "test_state_assign_owner_endpoint.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

reset_db.create_fresh_db(TEST_DB_PATH)

from ops_layer import app as app_module
from state_ledger import boundary as state_boundary


class TestStateAssignOwnerEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = app_module.app.test_client()

    def setUp(self) -> None:
        os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)
        reset_db.create_fresh_db(TEST_DB_PATH)

    def test_assign_owner_requires_planning_mode(self) -> None:
        payload = {
            "entity_ref": "org:demo/entity:project:alpha",
            "owner_actor_ref": "org:demo/actor:owner"
        }
        response = self.client.post(
            "/api/state/assign_owner",
            headers={"X-Ops-Mode": "execution"},
            json=payload
        )
        self.assertEqual(response.status_code, 400)
        body = response.get_json() or {}
        self.assertEqual(body.get("code"), "OPS_MODE_REQUIRED_PLANNING")
        self.assertIn("error", body)
        error_msg = body.get("error", "")
        self.assertIn("planning", error_msg.lower())

    def test_assign_owner_refuses_missing_entity(self) -> None:
        payload = {
            "entity_ref": "org:demo/entity:project:missing",
            "owner_actor_ref": "org:demo/actor:owner"
        }
        response = self.client.post(
            "/api/state/assign_owner",
            headers={"X-Ops-Mode": "planning"},
            json=payload
        )
        self.assertEqual(response.status_code, 400)
        body = response.get_json() or {}
        self.assertEqual(body.get("code"), "ENTITY_REF_NOT_REGISTERED")
        self.assertIn("error", body)
        error_msg = body.get("error", "")
        self.assertIn("entity_ref", error_msg.lower())

    def test_ensure_entity_with_owner_requires_planning_mode(self) -> None:
        payload = {
            "entity_ref": "org:demo/entity:project:alpha",
            "owner_actor_ref": "org:demo/actor:owner"
        }
        response = self.client.post(
            "/harness/ensure_entity_with_owner",
            headers={"X-Ops-Mode": "execution"},
            json=payload
        )
        self.assertEqual(response.status_code, 400)
        body = response.get_json() or {}
        self.assertEqual(body.get("code"), "OPS_MODE_REQUIRED_PLANNING")
        self.assertIn("error", body)
        error_msg = body.get("error", "")
        self.assertIn("planning", error_msg.lower())

    def test_ensure_entity_with_owner_creates_entity_and_owner(self) -> None:
        payload = {
            "entity_ref": "org:demo/entity:project:alpha",
            "owner_actor_ref": "org:demo/actor:owner"
        }
        response = self.client.post(
            "/harness/ensure_entity_with_owner",
            headers={"X-Ops-Mode": "planning"},
            json=payload
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json() or {}
        self.assertTrue(body.get("success"))
        self.assertTrue(body.get("entity_created"))
        self.assertTrue(body.get("owner_assigned"))

    def test_assign_owner_allows_state_declaration(self) -> None:
        entity_ref = "org:demo/entity:project:alpha"
        owner_ref = "org:demo/actor:owner"
        state_boundary.register_entity(entity_ref, "Alpha Project")

        declaration_payload = {
            "entity_ref": entity_ref,
            "scope_ref": "org:demo/scope:weekly",
            "state_text": "Operations continue.",
            "actor_ref": owner_ref,
            "declaration_kind": "REAFFIRMATION"
        }

        refusal = self.client.post(
            "/api/state/declarations",
            headers={"X-Ops-Mode": "planning"},
            json=declaration_payload
        )
        self.assertEqual(refusal.status_code, 400)
        refusal_msg = (refusal.get_json() or {}).get("error", "")
        self.assertIn("DS-2", refusal_msg)

        assign_payload = {
            "entity_ref": entity_ref,
            "owner_actor_ref": owner_ref
        }
        assigned = self.client.post(
            "/api/state/assign_owner",
            headers={"X-Ops-Mode": "planning"},
            json=assign_payload
        )
        self.assertEqual(assigned.status_code, 200)
        assigned_body = assigned.get_json() or {}
        self.assertTrue(assigned_body.get("success"))
        self.assertEqual(assigned_body.get("entity_ref"), entity_ref)
        self.assertEqual(assigned_body.get("owner_actor_ref"), owner_ref)
        self.assertIn("assignment_id", assigned_body)

        forbidden_fields = {
            "score",
            "rating",
            "blame",
            "interpretation",
            "assessment",
            "analysis"
        }
        self.assertTrue(forbidden_fields.isdisjoint(assigned_body.keys()))

        declared = self.client.post(
            "/api/state/declarations",
            headers={"X-Ops-Mode": "planning"},
            json=declaration_payload
        )
        self.assertEqual(declared.status_code, 200)
        declared_body = declared.get_json() or {}
        self.assertTrue(declared_body.get("success"))
        self.assertIsNotNone(declared_body.get("declaration_id"))

    @classmethod
    def tearDownClass(cls) -> None:
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        for suffix in ("-wal", "-shm"):
            extra = Path(str(TEST_DB_PATH) + suffix)
            if extra.exists():
                extra.unlink()


if __name__ == "__main__":
    unittest.main()
