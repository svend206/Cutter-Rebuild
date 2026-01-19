import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import database


class TestUnclosedQuotesAge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.test_db_path = Path(cls.test_dir) / "test_unclosed_quotes_age.db"
        os.environ["TEST_DB_PATH"] = str(cls.test_db_path)
        database.require_test_db("unclosed quotes age tests")

        result = subprocess.run(
            [sys.executable, "scripts/reset_db.py", "--db-path", str(cls.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode != 0:
            raise RuntimeError(f"reset_db failed: {result.stderr}")

    @classmethod
    def tearDownClass(cls):
        if cls.test_db_path.exists():
            cls.test_db_path.unlink()
        for suffix in ("-wal", "-shm"):
            extra = Path(str(cls.test_db_path) + suffix)
            if extra.exists():
                extra.unlink()

    def test_unclosed_quotes_include_age_days(self):
        unclosed = database.get_unclosed_quotes()
        if len(unclosed) == 0:
            self.skipTest("No quotes present in test database")
        for row in unclosed:
            self.assertIn("age_days", row)
            self.assertIsNotNone(row["age_days"])
            self.assertGreaterEqual(row["age_days"], 0)


if __name__ == "__main__":
    unittest.main()
