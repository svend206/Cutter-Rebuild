import os
import tempfile
import unittest
from pathlib import Path

# Ensure isolated DB before importing app/database
TEST_DB_PATH = Path(tempfile.gettempdir()) / "test_app_entrypoint.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

from scripts import reset_db

reset_db.create_fresh_db(TEST_DB_PATH)

import app as app_module


class AppEntrypointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = app_module.app.test_client()

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("status"), "ok")

    def test_system_health_endpoint(self) -> None:
        response = self.client.get("/api/system/health", headers={"X-Ops-Mode": "planning"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("status"), "healthy")
        self.assertEqual(payload.get("ping"), "pong")
        self.assertIn("metrics", payload)
        self.assertIn("system_info", payload)

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
