import os
import tempfile
import unittest
from pathlib import Path

from scripts import reset_db

TEST_DB_PATH = Path(tempfile.gettempdir()) / "test_ops_mode_guard.db"
os.environ["TEST_DB_PATH"] = str(TEST_DB_PATH)

reset_db.create_fresh_db(TEST_DB_PATH)

from ops_layer import app as ops_app_module


class OpsModeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = ops_app_module.app.test_client()

    def test_execution_mode_strips_metrics(self) -> None:
        response = self.client.get(
            "/api/system/health",
            headers={"X-Ops-Mode": "execution"}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsNotNone(payload)
        self.assertNotIn("metrics", payload)

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
