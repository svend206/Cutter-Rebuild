import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

# Ensure isolated DB before importing app/database
TEST_DB_PATH = Path(__file__).parent / "test_guild_export_payload.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

from scripts import reset_db

reset_db.create_fresh_db(TEST_DB_PATH)

from ops_layer import app as app_module


class GuildExportPayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)
        cls.client = app_module.app.test_client()

    def test_export_requires_actor_ref(self) -> None:
        response = self.client.post("/export_guild_packet", json={})
        self.assertEqual(response.status_code, 400)

    def test_export_payload_includes_provenance(self) -> None:
        os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)
        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ops__quote_history
            (filename, anchor_price, final_price, status, is_guild_submission,
             is_compliant, is_deleted, tag_weights, loss_reason, material, genesis_hash,
             process_routing, quote_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "part.step",
            100.0,
            120.0,
            "Won",
            1,
            1,
            0,
            '{"Rush Job": 15}',
            '["late response"]',
            "Aluminum 6061",
            "genesis_hash_123",
            '["3-Axis Mill"]',
            "Q-EXPORT-1"
        ))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        response = self.client.post(
            "/export_guild_packet",
            json={"actor_ref": "org:acme/actor:exporter"}
        )
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data.decode("utf-8"))
        response.close()
        self.assertIn("export_id", payload)
        self.assertEqual(payload["initiated_by_actor_ref"], "org:acme/actor:exporter")
        self.assertEqual(payload["source_system"], "ops_layer")
        self.assertEqual(payload["record_count"], 1)
        self.assertEqual(payload["records"][0]["source_table"], "ops__quote_history")
        self.assertEqual(payload["records"][0]["record"]["id"], record_id)

        conn = sqlite3.connect(str(TEST_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT exported_at FROM ops__quote_history WHERE id = ?", (record_id,))
        exported_at = cursor.fetchone()[0]
        conn.close()
        self.assertIsNotNone(exported_at)

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
