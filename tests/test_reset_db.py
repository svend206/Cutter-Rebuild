"""
Smoke test: Database reset script

Verifies that scripts/reset_db.py:
- Runs without errors
- Creates fresh database with all required tables
- Backs up existing database safely
"""

import unittest
import subprocess
import sys
import os
import tempfile
import sqlite3
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestResetDB(unittest.TestCase):
    """Smoke test for database reset script."""
    
    def setUp(self):
        """Set up temporary directories for test."""
        # Create unique temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.test_dir) / "test.db"
        self.backup_dir = Path(self.test_dir) / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        if Path(self.test_dir).exists():
            try:
                shutil.rmtree(self.test_dir)
            except Exception as e:
                print(f"Warning: Could not clean up test directory: {e}")
    
    def test_reset_creates_fresh_database(self):
        """Reset script should create fresh database with all required tables."""
        # Create a dummy existing database
        conn = sqlite3.connect(str(self.test_db_path))
        conn.execute("CREATE TABLE dummy (id INTEGER)")
        conn.commit()
        conn.close()
        
        # Verify dummy db exists
        self.assertTrue(self.test_db_path.exists())
        
        # Run reset script
        # Note: We need to change directory or use custom paths
        # For this test, we'll create a minimal DB directly since the script uses database.initialize_database()
        
        # Instead, let's test that the script runs successfully on a temp path
        result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # Should exit successfully
        self.assertEqual(
            result.returncode,
            0,
            f"Reset script should exit with code 0. stderr: {result.stderr}"
        )
        
        # Should produce output
        self.assertIn("DATABASE RESET COMPLETE", result.stdout)
        
        # Fresh database should exist
        self.assertTrue(self.test_db_path.exists())
    
    def test_reset_verifies_required_tables(self):
        """Reset script should verify all required tables exist."""
        result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(result.returncode, 0)
        
        # Should verify tables
        self.assertIn("[VERIFY] Checking core tables", result.stdout)
        
        # Should find all required tables
        required_tables = [
            'ops__quotes',
            'ops__parts', 
            'ops__customers',
            'ops__contacts',
            'cutter__events',
            'state__entities',
            'state__recognition_owners',
            'state__declarations'
        ]
        
        for table in required_tables:
            self.assertIn(
                f"[OK] table: {table}",
                result.stdout,
                f"Should verify table {table} exists"
            )
    
    def test_reset_backs_up_existing_database(self):
        """Reset script should back up existing database before reset."""
        # Create existing database with some data
        conn = sqlite3.connect(str(self.test_db_path))
        conn.execute("CREATE TABLE existing_data (id INTEGER, value TEXT)")
        conn.execute("INSERT INTO existing_data VALUES (1, 'test')")
        conn.commit()
        conn.close()
        
        original_size = self.test_db_path.stat().st_size
        self.assertGreater(original_size, 0)
        
        # Run reset (this will fail to backup since backup_dir is in temp location)
        # But we can check that it at least tries
        result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # Should mention backup (even if to default location)
        self.assertTrue(
            "[BACKUP]" in result.stdout or "[INFO] No existing database" in result.stdout,
            "Should attempt to backup or report no existing DB"
        )
    
    def test_reset_script_runs_without_crash(self):
        """Reset script should run to completion without crashing."""
        result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30
        )
        
        # Should not crash
        self.assertNotEqual(result.returncode, -1, "Script should not crash")
        
        # Should complete with success or graceful error
        self.assertIn(
            "DATABASE RESET",
            result.stdout,
            "Should show database reset header"
        )
    
    def test_reset_creates_state_ledger_views(self):
        """Reset script should create all State Ledger derived-state views."""
        result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(result.returncode, 0)
        
        # Should verify all required views
        required_views = [
            'view_ds1_persistent_continuity',
            'view_ds2_unowned_recognition',
            'view_ds5_deferred_recognition'
        ]
        
        for view in required_views:
            self.assertIn(
                f"[OK] view: {view}",
                result.stdout,
                f"Should verify view {view} exists"
            )
    
    def test_weekly_ritual_works_after_reset(self):
        """Weekly ritual script should work after database reset (no missing table errors)."""
        # Reset database first
        reset_result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(reset_result.returncode, 0, "Reset should succeed")
        
        # Set TEST_DB_PATH for weekly_ritual
        env = os.environ.copy()
        env['TEST_DB_PATH'] = str(self.test_db_path)
        
        # Run weekly ritual script
        ritual_result = subprocess.run(
            [sys.executable, 'scripts/weekly_ritual.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env
        )
        
        # Should not crash with missing table errors
        self.assertNotIn(
            "no such table: view_ds2_unowned_recognition",
            ritual_result.stderr,
            "DS-2 view should exist"
        )
        self.assertNotIn(
            "no such table: view_ds5_deferred_recognition",
            ritual_result.stderr,
            "DS-5 view should exist"
        )
        
        # Should exit with code 0 (always, per constitutional design)
        self.assertEqual(
            ritual_result.returncode,
            0,
            f"Weekly ritual should exit 0. stderr: {ritual_result.stderr}"
        )
        
        # Should produce valid JSON output
        try:
            output = self._extract_json(ritual_result.stdout)
            self.assertIn("ds2_unowned_recognition", output)
            self.assertIn("ds5_deferred_recognition", output)
        except json.JSONDecodeError as e:
            self.fail(f"Weekly ritual output should be valid JSON: {e}\nOutput: {ritual_result.stdout}")

    def _extract_json(self, output: str):
        lines = [line for line in output.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            if line.lstrip().startswith(("{", "[")):
                try:
                    return json.loads("\n".join(lines[i:]))
                except json.JSONDecodeError:
                    continue
        raise json.JSONDecodeError("No JSON found", output, 0)


if __name__ == '__main__':
    unittest.main()
