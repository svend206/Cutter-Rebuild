"""
Test Loop 1 cadence ritual demo script.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestLoop1RitualDemo(unittest.TestCase):
    def test_demo_script_outputs_raw_rows(self):
        temp_dir = tempfile.gettempdir()
        db_path = Path(temp_dir) / "test_loop1_ritual_demo.db"

        if db_path.exists():
            db_path.unlink()

        env = os.environ.copy()
        env["TEST_DB_PATH"] = str(db_path)

        result = subprocess.run(
            [sys.executable, 'scripts/loop1_ritual_demo.py', '--db-path', str(db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env
        )

        self.assertEqual(result.returncode, 0, result.stderr)

        lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), 2, "Expected two JSON outputs")

        first = json.loads(lines[0])
        second = json.loads(lines[1])

        first_refs = {row["entity_ref"] for row in first}
        second_refs = {row["entity_ref"] for row in second}

        self.assertIn("entity:demo", first_refs)
        self.assertNotIn("entity:demo", second_refs)
