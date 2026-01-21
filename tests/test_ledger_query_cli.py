"""
Test Ledger Query CLI (Smoke Tests)

Verifies CLI can be invoked and returns data without errors.
"""

import unittest
import subprocess
import sys
import os
import json
import tempfile
import sqlite3
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLedgerQueryCLI(unittest.TestCase):
    """Smoke tests for ledger query CLI."""
    
    def setUp(self):
        """Set up test database."""
        import database
        import time
        
        # Create isolated test database with unique name per run
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time() * 1000)
        self.test_db = Path(temp_dir) / f"test_query_cli_{timestamp}.db"
        
        # Ensure clean state (but this should be a new file each time)
        if self.test_db.exists():
            try:
                self.test_db.unlink()
            except PermissionError:
                # Use an even more unique name if file is locked
                import random
                timestamp = f"{timestamp}_{random.randint(1000, 9999)}"
                self.test_db = Path(temp_dir) / f"test_query_cli_{timestamp}.db"
        
        os.environ["TEST_DB_PATH"] = str(self.test_db)
        
        # Reload database module to pick up TEST_DB_PATH
        import importlib
        importlib.reload(database)
        database.require_test_db("ledger_query_cli test")
        
        # Initialize database (creates Ops + Cutter tables)
        database.initialize_database()
        
        # Verify Cutter tables exist and create if needed
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cutter__events'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE cutter__events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    subject_ref TEXT NOT NULL,
                    event_data TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    ingested_by_service TEXT NOT NULL,
                    ingested_by_version TEXT NOT NULL
                )
            """)
            conn.commit()
        conn.close()
        
        # Create State Ledger tables
        conn = sqlite3.connect(self.test_db)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS state__entities (
                entity_ref TEXT PRIMARY KEY,
                entity_label TEXT,
                cadence_days INTEGER NOT NULL DEFAULT 7,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS state__recognition_owners (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_ref TEXT NOT NULL,
                owner_actor_ref TEXT NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                unassigned_at TEXT,
                assigned_by_actor_ref TEXT NOT NULL,
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            );
            
            CREATE UNIQUE INDEX IF NOT EXISTS idx_current_owner 
            ON state__recognition_owners(entity_ref) 
            WHERE unassigned_at IS NULL;
            
            CREATE TABLE IF NOT EXISTS state__declarations (
                declaration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_ref TEXT NOT NULL,
                scope_ref TEXT NOT NULL,
                state_text TEXT NOT NULL,
                classification TEXT,
                declared_by_actor_ref TEXT NOT NULL,
                declared_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                declaration_kind TEXT NOT NULL CHECK (declaration_kind IN ('REAFFIRMATION','RECLASSIFICATION')),
                supersedes_declaration_id INTEGER,
                cutter_evidence_ref TEXT,
                evidence_refs_json TEXT DEFAULT '[]',
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            );
            
            -- DS-1 View (simplified for testing)
            CREATE VIEW IF NOT EXISTS view_ds1_persistent_continuity AS
            SELECT 
                entity_ref,
                scope_ref,
                2 as consecutive_reaffirmations,
                MIN(declared_at) as first_reaffirmed_at,
                MAX(declared_at) as last_reaffirmed_at
            FROM state__declarations
            WHERE declaration_kind = 'REAFFIRMATION'
            GROUP BY entity_ref, scope_ref
            HAVING COUNT(*) > 1;
            
            -- DS-2 View
            CREATE VIEW IF NOT EXISTS view_ds2_unowned_recognition AS
            SELECT 
                e.entity_ref,
                e.entity_label,
                e.cadence_days,
                e.created_at as entity_created_at
            FROM state__entities e
            WHERE NOT EXISTS (
                SELECT 1 FROM state__recognition_owners o
                WHERE o.entity_ref = e.entity_ref
                AND o.unassigned_at IS NULL
            );
            
            -- DS-5 View
            CREATE VIEW IF NOT EXISTS view_ds5_deferred_recognition AS
            SELECT 
                e.entity_ref,
                e.entity_label,
                e.cadence_days,
                MAX(d.declared_at) as last_declaration_at,
                CAST(
                    (julianday('now') - julianday(MAX(d.declared_at))) 
                    AS INTEGER
                ) as days_since_last_declaration
            FROM state__entities e
            LEFT JOIN state__declarations d ON e.entity_ref = d.entity_ref
            GROUP BY e.entity_ref, e.entity_label, e.cadence_days
            HAVING days_since_last_declaration > e.cadence_days;
        """)
        conn.commit()
        conn.close()
        
        # Seed minimal test data (direct SQL to avoid module DB_PATH issues)
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # State Ledger test data
        cursor.execute("""
            INSERT INTO state__entities (entity_ref, entity_label, cadence_days)
            VALUES ('org:test/entity:customer:c1', 'Test Customer 1', 7)
        """)
        
        cursor.execute("""
            INSERT INTO state__recognition_owners 
            (entity_ref, owner_actor_ref, assigned_by_actor_ref)
            VALUES ('org:test/entity:customer:c1', 'org:test/actor:alice', 'org:test/actor:admin')
        """)
        
        cursor.execute("""
            INSERT INTO state__declarations 
            (entity_ref, scope_ref, state_text, declared_by_actor_ref, declaration_kind)
            VALUES ('org:test/entity:customer:c1', 'org:test/scope:weekly', 
                    'Customer is active', 'org:test/actor:alice', 'RECLASSIFICATION')
        """)
        
        # Cutter Ledger test data
        cursor.execute("""
            INSERT INTO cutter__events 
            (event_type, subject_ref, event_data, ingested_by_service, ingested_by_version)
            VALUES ('quote_created', 'quote:1', '{"test": "data"}', 'test_cli', 'v1')
        """)
        
        conn.commit()
        conn.close()
        
        self.cli_script = Path(__file__).parent.parent / "scripts" / "ledger_query_cli.py"
    
    def tearDown(self):
        """Clean up test database."""
        # Multiple attempts to delete with delays
        import time
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                if self.test_db.exists():
                    self.test_db.unlink()
                break
            except PermissionError:
                if attempt < max_attempts - 1:
                    time.sleep(0.2)
                else:
                    # If we still can't delete after all attempts, just pass
                    # (Windows file locking can be stubborn)
                    pass
    
    def _build_cli_env(self):
        env = os.environ.copy()
        if not self.test_db:
            raise AssertionError("TEST_DB_PATH is required for CLI tests.")
        os.environ["TEST_DB_PATH"] = str(self.test_db)
        env["TEST_DB_PATH"] = str(self.test_db)
        import database
        resolved = database.resolve_db_path()
        if Path(resolved).resolve() != Path(self.test_db).resolve():
            raise AssertionError("database.resolve_db_path must point to the test database.")
        return env

    def run_cli(self, *args):
        """Run CLI and return (stdout, stderr, returncode)."""
        env = self._build_cli_env()
        
        result = subprocess.run(
            [sys.executable, str(self.cli_script)] + list(args),
            capture_output=True,
            text=True,
            env=env
        )
        
        return result.stdout, result.stderr, result.returncode

    def parse_json_output(self, stdout: str):
        lines = [line for line in stdout.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            if line.lstrip().startswith(("{", "[")):
                try:
                    return json.loads("\n".join(lines[i:]))
                except json.JSONDecodeError:
                    continue
        raise ValueError("No JSON output found")
    
    def test_state_list_entities(self):
        """CLI should list entities."""
        stdout, stderr, returncode = self.run_cli("state", "list-entities")
        
        self.assertEqual(returncode, 0, f"CLI failed: {stderr}")
        
        # Parse JSON output
        data = self.parse_json_output(stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Should return at least one entity")
        
        # Check structure
        entity = data[0]
        self.assertIn('entity_ref', entity)
        self.assertIn('entity_label', entity)
        self.assertIn('cadence_days', entity)
    
    def test_state_declarations(self):
        """CLI should query declarations."""
        stdout, stderr, returncode = self.run_cli(
            "state", "declarations", 
            "--entity_ref", "org:test/entity:customer:c1"
        )
        
        self.assertEqual(returncode, 0, f"CLI failed: {stderr}")
        
        data = self.parse_json_output(stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Should return at least one declaration")
        
        # Check structure
        decl = data[0]
        self.assertIn('declaration_id', decl)
        self.assertIn('entity_ref', decl)
        self.assertIn('state_text', decl)
    
    def test_state_ds2(self):
        """CLI should query DS-2 (unowned entities)."""
        stdout, stderr, returncode = self.run_cli("state", "ds2")
        
        self.assertEqual(returncode, 0, f"CLI failed: {stderr}")
        
        data = self.parse_json_output(stdout)
        self.assertIsInstance(data, list)
        # May be empty if all entities have owners, which is fine
    
    def test_cutter_events(self):
        """CLI should query Cutter Ledger events."""
        stdout, stderr, returncode = self.run_cli("cutter", "events")
        
        self.assertEqual(returncode, 0, f"CLI failed: {stderr}")
        
        data = self.parse_json_output(stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Should return at least one event")
        
        # Check structure
        event = data[0]
        self.assertIn('id', event)
        self.assertIn('event_type', event)
        self.assertIn('subject_ref', event)
    
    def test_cutter_events_with_filter(self):
        """CLI should filter Cutter Ledger events."""
        stdout, stderr, returncode = self.run_cli(
            "cutter", "events",
            "--subject_ref", "quote:1"
        )
        
        self.assertEqual(returncode, 0, f"CLI failed: {stderr}")
        
        data = self.parse_json_output(stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Should return filtered events")
        
        # All events should match filter
        for event in data:
            self.assertEqual(event['subject_ref'], "quote:1")
    
    def test_cli_no_args_shows_help(self):
        """CLI with no args should show help."""
        stdout, stderr, returncode = self.run_cli()
        
        self.assertNotEqual(returncode, 0, "Should return non-zero with no args")
        self.assertTrue(
            "usage:" in stdout.lower() or "usage:" in stderr.lower(),
            "Should show usage help"
        )


if __name__ == '__main__':
    unittest.main()
