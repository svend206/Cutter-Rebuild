"""
Test: State Ledger Schema Consistency

Verifies that state__declarations table has all required columns
and that CLI queries work correctly.
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


class TestStateSchema(unittest.TestCase):
    """Test State Ledger schema consistency."""
    
    def setUp(self):
        """Set up temporary database for testing."""
        # Create unique temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.test_dir) / "test.db"
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        if Path(self.test_dir).exists():
            try:
                shutil.rmtree(self.test_dir)
            except Exception as e:
                print(f"Warning: Could not clean up test directory: {e}")
    
    def test_reset_db_creates_classification_column(self):
        """Reset script should create state__declarations with classification column."""
        # Run reset script
        result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(result.returncode, 0, f"Reset should succeed. stderr: {result.stderr}")
        
        # Verify classification column exists
        conn = sqlite3.connect(str(self.test_db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(state__declarations)")
        columns = [row[1] for row in cursor.fetchall()]
        
        self.assertIn('classification', columns, "classification column should exist")
        self.assertIn('declaration_kind', columns, "declaration_kind column should exist")
        
        conn.close()
    
    def test_classification_column_nullable(self):
        """classification column should be nullable."""
        # Run reset script
        subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db_path)],
            capture_output=True,
            cwd=Path(__file__).parent.parent
        )
        
        conn = sqlite3.connect(str(self.test_db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(state__declarations)")
        for row in cursor.fetchall():
            if row[1] == 'classification':
                is_notnull = row[3]
                self.assertEqual(is_notnull, 0, "classification should be nullable (notnull=0)")
                break
        else:
            self.fail("classification column not found")
        
        conn.close()
    
    def test_declaration_kind_not_null(self):
        """declaration_kind column should be NOT NULL."""
        # Run reset script
        subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', str(self.test_db_path)],
            capture_output=True,
            cwd=Path(__file__).parent.parent
        )
        
        conn = sqlite3.connect(str(self.test_db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(state__declarations)")
        for row in cursor.fetchall():
            if row[1] == 'declaration_kind':
                is_notnull = row[3]
                self.assertEqual(is_notnull, 1, "declaration_kind should be NOT NULL (notnull=1)")
                break
        else:
            self.fail("declaration_kind column not found")
        
        conn.close()


class TestStateCLI(unittest.TestCase):
    """Test State Ledger CLI commands."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database for CLI tests."""
        import time
        import random
        unique_suffix = f"_test_{int(time.time())}_{random.randint(1000, 9999)}"
        cls.test_db = tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'{unique_suffix}.db',
            delete=False
        )
        cls.test_db_path = cls.test_db.name
        cls.test_db.close()
        
        # Initialize database
        result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py', '--db-path', cls.test_db_path],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to initialize test database: {result.stderr}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        import time
        time.sleep(0.1)
        
        if os.path.exists(cls.test_db_path):
            try:
                os.unlink(cls.test_db_path)
            except Exception as e:
                print(f"Warning: Could not delete test database: {e}")
    
    def test_latest_declarations_cli_runs(self):
        """CLI latest-declarations command should run without error."""
        env = self._build_cli_env()
        
        result = subprocess.run(
            [sys.executable, 'scripts/ledger_query_cli.py', 'state', 'latest-declarations', '--limit', '5'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )
        
        # Should exit with code 0
        self.assertEqual(
            result.returncode,
            0,
            f"CLI should exit 0. stderr: {result.stderr}"
        )
        
        # Should produce valid JSON
        try:
            output = self._extract_json(result.stdout)
            self.assertIsInstance(output, list, "Output should be a list")
        except json.JSONDecodeError as e:
            self.fail(f"Output should be valid JSON: {e}\nOutput: {result.stdout}")
    
    def test_latest_declarations_includes_declaration_kind(self):
        """CLI output should include declaration_kind field."""
        env = self._build_cli_env()
        
        result = subprocess.run(
            [sys.executable, 'scripts/ledger_query_cli.py', 'state', 'latest-declarations', '--limit', '1'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0)
        
        output = self._extract_json(result.stdout)
        
        if len(output) > 0:
            # If there are declarations, they should have declaration_kind
            first_declaration = output[0]
            self.assertIn(
                'declaration_kind',
                first_declaration,
                "Declaration should include declaration_kind field"
            )
            self.assertIn(
                'classification',
                first_declaration,
                "Declaration should include classification field (even if null)"
            )

    def _extract_json(self, output: str):
        lines = [line for line in output.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            if line.lstrip().startswith(("{", "[")):
                try:
                    return json.loads("\n".join(lines[i:]))
                except json.JSONDecodeError:
                    continue
        raise json.JSONDecodeError("No JSON found", output, 0)

    def _build_cli_env(self):
        if not self.test_db_path:
            raise AssertionError("TEST_DB_PATH is required for CLI tests.")
        os.environ["TEST_DB_PATH"] = self.test_db_path
        env = os.environ.copy()
        env['TEST_DB_PATH'] = self.test_db_path
        import database
        resolved = database.resolve_db_path()
        if Path(resolved).resolve() != Path(self.test_db_path).resolve():
            raise AssertionError("database.resolve_db_path must point to the test database.")
        return env


if __name__ == '__main__':
    unittest.main()
