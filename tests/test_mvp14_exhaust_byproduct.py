import json
import os
import sqlite3
import unittest
from pathlib import Path

# Ensure isolated DB before importing app/database
TEST_DB_PATH = Path(__file__).parent / "test_mvp14_exhaust_byproduct.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

from scripts import reset_db

reset_db.create_fresh_db(TEST_DB_PATH)

from ops_layer import app as app_module


class TestMVP14ExhaustByproduct(unittest.TestCase):
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

    def _save_quote(self):
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
        return self.client.post("/save_quote", json=payload)

    def _fetch_latest_status_event(self):
        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_data
            FROM cutter__events
            WHERE event_type = 'QUOTE_STATUS_CHANGED'
            ORDER BY id DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def test_save_quote_succeeds_without_explanations(self) -> None:
        before_events = self._count_cutter_events()
        response = self._save_quote()
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body.get("success"))
        self.assertGreater(self._count_cutter_events(), before_events)

    def test_quote_status_update_without_explanations(self) -> None:
        create_response = self._save_quote()
        self.assertEqual(create_response.status_code, 200)
        body = create_response.get_json()
        quote_id = body.get("id")
        self.assertIsNotNone(quote_id)

        before_events = self._count_cutter_events()
        update_response = self.client.post(
            f"/api/quote/{quote_id}/update_status",
            json={"status": "Sent"}
        )
        self.assertEqual(update_response.status_code, 200)
        update_body = update_response.get_json()
        self.assertTrue(update_body.get("success"))
        self.assertGreater(self._count_cutter_events(), before_events)

        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT win_notes, loss_reason
            FROM ops__quotes
            WHERE id = ?
        """, (quote_id,))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertIsNone(row[0])
        self.assertIsNone(row[1])

        event_data_raw = self._fetch_latest_status_event()
        self.assertIsNotNone(event_data_raw)
        event_data = json.loads(event_data_raw)
        self.assertNotIn("win_notes", event_data)
        self.assertNotIn("loss_reason", event_data)


if __name__ == "__main__":
    unittest.main()
