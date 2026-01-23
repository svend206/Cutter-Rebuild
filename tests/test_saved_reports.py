import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts import reset_db
from state_ledger import boundary as state_boundary


class TestSavedReportsPlanningOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_db_path = Path(tempfile.gettempdir()) / "test_saved_reports.db"
        os.environ["TEST_DB_PATH"] = str(cls.test_db_path)
        reset_db.create_fresh_db(cls.test_db_path)
        from ops_layer import app as app_module
        cls.client = app_module.app.test_client()

    def setUp(self) -> None:
        os.environ["TEST_DB_PATH"] = str(self.test_db_path)
        reset_db.create_fresh_db(self.test_db_path)

    def _seed_state_declaration(self) -> None:
        entity_ref = "org:demo/entity:project:alpha"
        owner_ref = "org:demo/actor:owner"
        admin_ref = "org:demo/actor:admin"
        state_boundary.register_entity(entity_ref, "Alpha Project", cadence_days=7)
        state_boundary.assign_owner(entity_ref, owner_ref, admin_ref)
        state_boundary.emit_state_declaration(
            entity_ref=entity_ref,
            scope_ref="org:demo/scope:weekly",
            state_text="Running",
            actor_ref=owner_ref,
            declaration_kind="REAFFIRMATION"
        )

    def _count_table(self, table_name: str) -> int:
        conn = sqlite3.connect(str(self.test_db_path))
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def test_reports_refuse_execution_mode(self) -> None:
        payload = {
            "report_name": "weekly-latest",
            "query_type": "latest_declaration_per_entity",
            "params": {},
            "created_by_actor_ref": "org:demo/actor:owner"
        }
        save_response = self.client.post(
            "/api/reports/save",
            headers={"X-Ops-Mode": "execution"},
            json=payload
        )
        self.assertEqual(save_response.status_code, 400)
        self.assertEqual((save_response.get_json() or {}).get("code"), "OPS_MODE_REQUIRED_PLANNING")

        list_response = self.client.get(
            "/api/reports/list",
            headers={"X-Ops-Mode": "execution"}
        )
        self.assertEqual(list_response.status_code, 400)
        self.assertEqual((list_response.get_json() or {}).get("code"), "OPS_MODE_REQUIRED_PLANNING")

        run_response = self.client.post(
            "/api/reports/run",
            headers={"X-Ops-Mode": "execution"},
            json={"report_id": 1}
        )
        self.assertEqual(run_response.status_code, 400)
        self.assertEqual((run_response.get_json() or {}).get("code"), "OPS_MODE_REQUIRED_PLANNING")

    def test_save_and_list_reports(self) -> None:
        payload = {
            "report_name": "weekly-latest",
            "query_type": "latest_declaration_per_entity",
            "params": {},
            "created_by_actor_ref": "org:demo/actor:owner"
        }
        save_response = self.client.post(
            "/api/reports/save",
            headers={"X-Ops-Mode": "planning"},
            json=payload
        )
        self.assertEqual(save_response.status_code, 200)
        body = save_response.get_json() or {}
        self.assertTrue(body.get("success"))

        list_response = self.client.get(
            "/api/reports/list",
            headers={"X-Ops-Mode": "planning"}
        )
        self.assertEqual(list_response.status_code, 200)
        reports = (list_response.get_json() or {}).get("reports", [])
        names = [report.get("report_name") for report in reports]
        self.assertIn("weekly-latest", names)

    def test_run_report_read_only_and_schema(self) -> None:
        self._seed_state_declaration()
        payload = {
            "report_name": "weekly-latest",
            "query_type": "latest_declaration_per_entity",
            "params": {},
            "created_by_actor_ref": "org:demo/actor:owner"
        }
        save_response = self.client.post(
            "/api/reports/save",
            headers={"X-Ops-Mode": "planning"},
            json=payload
        )
        report = (save_response.get_json() or {}).get("report", {})
        report_id = report.get("report_id")
        self.assertIsNotNone(report_id)

        before_state = self._count_table("state__declarations")
        before_events = self._count_table("cutter__events")

        run_response = self.client.post(
            "/api/reports/run",
            headers={"X-Ops-Mode": "planning"},
            json={"report_id": report_id}
        )
        self.assertEqual(run_response.status_code, 200)
        body = run_response.get_json() or {}
        self.assertTrue(body.get("success"))
        rows = body.get("rows", [])
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)

        after_state = self._count_table("state__declarations")
        after_events = self._count_table("cutter__events")
        self.assertEqual(before_state, after_state)
        self.assertEqual(before_events, after_events)

        expected_keys = {
            "entity_ref",
            "entity_label",
            "cadence_days",
            "scope_ref",
            "state_text",
            "declaration_kind",
            "declared_by_actor_ref",
            "declared_at",
            "days_since_declaration"
        }
        forbidden_keys = {"status", "severity", "priority", "health", "score", "rating"}
        for row in rows:
            self.assertTrue(set(row.keys()).issubset(expected_keys))
            self.assertTrue(forbidden_keys.isdisjoint(set(row.keys())))


if __name__ == "__main__":
    unittest.main()
