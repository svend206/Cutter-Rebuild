"""
Test: Ledger Query CLI is Read-Only

Constitutional enforcement: Query CLI must NEVER write, migrate, 
initialize, or reset the database. It may only read from existing databases.
"""

import unittest
import subprocess
import sys
import os
import tempfile
import sqlite3
import time
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestQueryCLIReadOnly(unittest.TestCase):
    """Test that ledger query CLI is strictly read-only."""
    
    def setUp(self):
        """Set up temporary database with known declarations."""
        # Create unique temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.test_dir) / "test.db"
        os.environ["TEST_DB_PATH"] = str(self.test_db_path)
        import database
        database.require_test_db("query_cli_readonly test")
        
        # Create minimal database with State Ledger tables
        self._create_test_database()
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        if Path(self.test_dir).exists():
            try:
                shutil.rmtree(self.test_dir)
            except Exception as e:
                print(f"Warning: Could not clean up test directory: {e}")
    
    def _create_test_database(self):
        """Create minimal test database with State Ledger schema."""
        conn = sqlite3.connect(str(self.test_db_path))
        cursor = conn.cursor()
        
        # Create minimal State Ledger schema
        cursor.execute("""
            CREATE TABLE state__entities (
                entity_ref TEXT PRIMARY KEY,
                entity_label TEXT NOT NULL,
                cadence_days INTEGER NOT NULL DEFAULT 7,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE state__recognition_owners (
                entity_ref TEXT NOT NULL,
                owner_actor_ref TEXT NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
                unassigned_at TEXT,
                assigned_by_actor_ref TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE state__declarations (
                declaration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_ref TEXT NOT NULL,
                scope_ref TEXT NOT NULL,
                state_text TEXT NOT NULL,
                declaration_kind TEXT NOT NULL,
                declared_by_actor_ref TEXT NOT NULL,
                declared_at TEXT NOT NULL DEFAULT (datetime('now')),
                supersedes_declaration_id INTEGER,
                cutter_evidence_ref TEXT,
                classification TEXT
            )
        """)
        
        # Insert test entity
        cursor.execute("""
            INSERT INTO state__entities (entity_ref, entity_label, cadence_days)
            VALUES ('org:test/entity:machine:test', 'Test Machine', 7)
        """)
        
        # Insert test declaration
        cursor.execute("""
            INSERT INTO state__declarations 
            (entity_ref, scope_ref, state_text, declaration_kind, declared_by_actor_ref)
            VALUES ('org:test/entity:machine:test', 'org:test/scope:daily', 
                    'Machine is operational', 'RECLASSIFICATION', 'org:test/actor:operator')
        """)
        
        conn.commit()
        conn.close()

    def _build_cli_env(self, db_path: Path):
        if not db_path:
            raise AssertionError("TEST_DB_PATH is required for CLI tests.")
        os.environ["TEST_DB_PATH"] = str(db_path)
        env = os.environ.copy()
        env['TEST_DB_PATH'] = str(db_path)
        import database
        resolved = database.resolve_db_path()
        if Path(resolved).resolve() != Path(db_path).resolve():
            raise AssertionError("database.resolve_db_path must point to the test database.")
        return env
    
    def test_cli_does_not_modify_database(self):
        """Query CLI should not modify database (file size/timestamp unchanged)."""
        # Get initial file stats
        initial_size = self.test_db_path.stat().st_size
        initial_mtime = self.test_db_path.stat().st_mtime
        
        # Wait a moment to ensure timestamp would change if file modified
        time.sleep(0.1)
        
        # Run query CLI
        env = self._build_cli_env(self.test_db_path)
        
        result = subprocess.run(
            [sys.executable, 'scripts/ledger_query_cli.py', 'state', 'list-entities'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )
        
        # Get final file stats
        final_size = self.test_db_path.stat().st_size
        final_mtime = self.test_db_path.stat().st_mtime
        
        # Verify no modification
        self.assertEqual(initial_size, final_size, "Database file size should not change")
        self.assertEqual(initial_mtime, final_mtime, "Database file timestamp should not change")
        self.assertEqual(result.returncode, 0, "CLI should exit successfully")
    
    def test_cli_returns_valid_json(self):
        """Query CLI should return valid JSON output."""
        env = self._build_cli_env(self.test_db_path)
        
        result = subprocess.run(
            [sys.executable, 'scripts/ledger_query_cli.py', 'state', 'latest-declarations', '--limit', '5'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0, f"CLI should exit 0. stderr: {result.stderr}")
        
        # Verify valid JSON
        import json
        try:
            output = self._extract_json(result.stdout)
            self.assertIsInstance(output, list, "Output should be a list")
            
            # Should have our test declaration
            if len(output) > 0:
                self.assertIn('declaration_id', output[0])
                self.assertIn('state_text', output[0])
        except json.JSONDecodeError as e:
            self.fail(f"Output should be valid JSON: {e}\nOutput: {result.stdout}")
    
    def test_cli_refuses_if_database_missing(self):
        """Query CLI should refuse to run if database doesn't exist."""
        # Point to non-existent database
        non_existent = Path(self.test_dir) / "test_does_not_exist.db"
        
        env = self._build_cli_env(non_existent)
        
        result = subprocess.run(
            [sys.executable, 'scripts/ledger_query_cli.py', 'state', 'list-entities'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )
        
        # Should exit with error
        self.assertNotEqual(result.returncode, 0, "CLI should refuse to run without database")
        
        # Error should mention database not found
        self.assertIn("Database not found", result.stderr, "Error should mention missing database")
        self.assertIn("read-only", result.stderr.lower(), "Error should mention read-only constraint")
    
    def test_cli_does_not_import_reset_modules(self):
        """Query CLI should not import reset_db or test_setup modules."""
        # This is tested at runtime by the FORBIDDEN_IMPORTS guard
        # Here we verify the guard works by checking module names
        
        env = self._build_cli_env(self.test_db_path)
        
        # Run CLI (should work normally)
        result = subprocess.run(
            [sys.executable, 'scripts/ledger_query_cli.py', 'state', 'list-entities'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env,
            timeout=10
        )
        
        # Should succeed (no forbidden imports)
        self.assertEqual(result.returncode, 0)
        
        # Output should not mention CONSTITUTIONAL VIOLATION
        self.assertNotIn("CONSTITUTIONAL VIOLATION", result.stderr)

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
