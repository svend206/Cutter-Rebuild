"""
Smoke test: Weekly ritual script

Verifies that scripts/weekly_ritual.py:
- Runs without errors
- Exits with code 0
- Produces valid JSON output
- Contains DS-2 and DS-5 sections

Constitutional compliance:
- No summaries or advice in output
- Raw data only
"""

import unittest
import subprocess
import sys
import os
import json
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestWeeklyRitual(unittest.TestCase):
    """Smoke test for weekly ritual script."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        # Create unique temporary test database
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
        
        # Set TEST_DB_PATH environment variable
        os.environ['TEST_DB_PATH'] = cls.test_db_path
        
        # Initialize database with State Ledger schema
        import database
        import importlib
        importlib.reload(database)
        database.require_test_db("weekly_ritual test")
        
        database.initialize_database()
        
        # Create State Ledger tables
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Create state__entities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state__entities (
                entity_ref TEXT PRIMARY KEY,
                entity_label TEXT NOT NULL,
                cadence_days INTEGER NOT NULL DEFAULT 7,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Create state__recognition_owners
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state__recognition_owners (
                entity_ref TEXT NOT NULL,
                owner_actor_ref TEXT NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
                unassigned_at TEXT,
                assigned_by_actor_ref TEXT NOT NULL,
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            )
        """)
        
        # Create unique index for current owner
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_one_current_owner
            ON state__recognition_owners(entity_ref)
            WHERE unassigned_at IS NULL
        """)
        
        # Create state__declarations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state__declarations (
                declaration_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_ref TEXT NOT NULL,
                scope_ref TEXT NOT NULL,
                state_text TEXT NOT NULL,
                declaration_kind TEXT NOT NULL CHECK (declaration_kind IN ('REAFFIRMATION','RECLASSIFICATION')),
                declared_by_actor_ref TEXT NOT NULL,
                declared_at TEXT NOT NULL DEFAULT (datetime('now')),
                supersedes_declaration_id INTEGER,
                cutter_evidence_ref TEXT,
                evidence_refs_json TEXT DEFAULT '[]',
                FOREIGN KEY (entity_ref) REFERENCES state__entities(entity_ref)
            )
        """)
        
        # Create DS-2 view (Unowned Recognition)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS view_ds2_unowned_recognition AS
            SELECT 
                e.entity_ref,
                e.entity_label,
                e.cadence_days,
                e.created_at as entity_created_at
            FROM state__entities e
            WHERE e.entity_ref NOT IN (
                SELECT entity_ref 
                FROM state__recognition_owners 
                WHERE unassigned_at IS NULL
            )
        """)
        
        # Create DS-5 view (Deferred Recognition)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS view_ds5_deferred_recognition AS
            SELECT 
                e.entity_ref,
                e.entity_label,
                e.cadence_days,
                MAX(d.declared_at) as last_declaration_at,
                CAST((julianday('now') - julianday(MAX(d.declared_at))) AS INTEGER) as days_since_last_declaration
            FROM state__entities e
            INNER JOIN state__declarations d ON e.entity_ref = d.entity_ref
            WHERE e.entity_ref IN (
                SELECT entity_ref 
                FROM state__recognition_owners 
                WHERE unassigned_at IS NULL
            )
            GROUP BY e.entity_ref, e.entity_label, e.cadence_days
            HAVING CAST((julianday('now') - julianday(MAX(d.declared_at))) AS INTEGER) > e.cadence_days
        """)
        
        # Create Cutter Ledger table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cutter__events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                subject_ref TEXT NOT NULL,
                event_data TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                ingested_by_service TEXT,
                ingested_by_version TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Seed test data
        cls._seed_test_data()
    
    @classmethod
    def _seed_test_data(cls):
        """Seed minimal test data for DS-2 and DS-5."""
        import database
        from state_ledger.boundary import register_entity, assign_owner, emit_state_declaration
        from cutter_ledger.boundary import emit_cutter_event
        from datetime import datetime, timedelta
        
        # Create entity with owner and recent declaration (NOT in DS-5)
        register_entity(
            entity_ref="org:test-shop/entity:customer:active",
            entity_label="Active Entity",
            cadence_days=7
        )
        assign_owner(
            entity_ref="org:test-shop/entity:customer:active",
            owner_actor_ref="org:test-shop/actor:owner",
            assigned_by_actor_ref="org:test-shop/actor:admin"
        )
        emit_state_declaration(
            entity_ref="org:test-shop/entity:customer:active",
            scope_ref="org:test-shop/scope:weekly",
            state_text="Entity is active with recent recognition",
            actor_ref="org:test-shop/actor:owner",
            declaration_kind="RECLASSIFICATION"
        )
        
        # Create entity with owner but OLD declaration (IN DS-5)
        register_entity(
            entity_ref="org:test-shop/entity:customer:deferred",
            entity_label="Deferred Entity",
            cadence_days=7
        )
        assign_owner(
            entity_ref="org:test-shop/entity:customer:deferred",
            owner_actor_ref="org:test-shop/actor:owner",
            assigned_by_actor_ref="org:test-shop/actor:admin"
        )
        
        # Insert old declaration directly to force DS-5 state
        conn = database.get_connection()
        cursor = conn.cursor()
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        cursor.execute("""
            INSERT INTO state__declarations 
            (entity_ref, scope_ref, state_text, declaration_kind, declared_by_actor_ref, declared_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "org:test-shop/entity:customer:deferred",
            "org:test-shop/scope:weekly",
            "Entity recognition is overdue",
            "RECLASSIFICATION",
            "org:test-shop/actor:owner",
            old_date
        ))
        conn.commit()
        conn.close()
        
        # Create entity with NO owner (IN DS-2)
        register_entity(
            entity_ref="org:test-shop/entity:customer:unowned",
            entity_label="Unowned Entity",
            cadence_days=7
        )
        
        # Emit some Cutter events
        emit_cutter_event(
            event_type="TEST_EVENT_1",
            subject_ref="test:1",
            event_data={"test": "data"}
        )
        emit_cutter_event(
            event_type="TEST_EVENT_2",
            subject_ref="test:2",
            event_data={"test": "data"}
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        import time
        import gc
        gc.collect()
        time.sleep(0.1)
        
        if os.path.exists(cls.test_db_path):
            try:
                os.unlink(cls.test_db_path)
            except Exception as e:
                print(f"Warning: Could not delete test database: {e}")
    
    def test_weekly_ritual_runs_successfully(self):
        """Weekly ritual script should run and exit with code 0."""
        env = os.environ.copy()
        env['TEST_DB_PATH'] = self.test_db_path
        
        result = subprocess.run(
            [sys.executable, 'scripts/weekly_ritual.py'],
            capture_output=True,
            text=True,
            env=env,
            cwd=Path(__file__).parent.parent
        )
        
        # Should exit with code 0 (visibility, not enforcement)
        self.assertEqual(
            result.returncode, 
            0, 
            f"Weekly ritual should exit with code 0. stderr: {result.stderr}"
        )
        
        # Should produce output
        self.assertTrue(len(result.stdout) > 0, "Should produce output")
    
    def test_weekly_ritual_produces_valid_json(self):
        """Weekly ritual output should be valid JSON."""
        env = os.environ.copy()
        env['TEST_DB_PATH'] = self.test_db_path
        
        result = subprocess.run(
            [sys.executable, 'scripts/weekly_ritual.py'],
            capture_output=True,
            text=True,
            env=env,
            cwd=Path(__file__).parent.parent
        )
        
        # Parse JSON
        try:
            data = self._extract_json(result.stdout)
        except json.JSONDecodeError as e:
            self.fail(f"Output is not valid JSON: {e}\nOutput: {result.stdout}")
        
        # Verify structure
        self.assertIn('ritual', data)
        self.assertEqual(data['ritual'], 'weekly_structural_visibility')
        self.assertIn('timestamp', data)
        self.assertIn('constitutional_note', data)
    
    def test_weekly_ritual_contains_ds2_and_ds5(self):
        """Weekly ritual should contain DS-2 and DS-5 sections."""
        env = os.environ.copy()
        env['TEST_DB_PATH'] = self.test_db_path
        
        result = subprocess.run(
            [sys.executable, 'scripts/weekly_ritual.py'],
            capture_output=True,
            text=True,
            env=env,
            cwd=Path(__file__).parent.parent
        )
        
        data = self._extract_json(result.stdout)
        
        # Should have DS-2 section
        self.assertIn('ds2_unowned_recognition', data)
        self.assertIn('count', data['ds2_unowned_recognition'])
        self.assertIn('entities', data['ds2_unowned_recognition'])
        
        # Should have DS-5 section
        self.assertIn('ds5_deferred_recognition', data)
        self.assertIn('count', data['ds5_deferred_recognition'])
        self.assertIn('entities', data['ds5_deferred_recognition'])
        
        # DS-2 should find our unowned entity (at least 1)
        self.assertGreaterEqual(
            data['ds2_unowned_recognition']['count'],
            1,
            "Should find at least 1 unowned entity (org:test-shop/entity:customer:unowned)"
        )
        
        # DS-5 should find our deferred entity (at least 1)
        self.assertGreaterEqual(
            data['ds5_deferred_recognition']['count'],
            1,
            "Should find at least 1 deferred entity (org:test-shop/entity:customer:deferred)"
        )
    
    def test_weekly_ritual_with_events_flag(self):
        """Weekly ritual with --events flag should include Cutter events."""
        env = os.environ.copy()
        env['TEST_DB_PATH'] = self.test_db_path
        
        result = subprocess.run(
            [sys.executable, 'scripts/weekly_ritual.py', '--events', '10'],
            capture_output=True,
            text=True,
            env=env,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(result.returncode, 0)
        
        data = self._extract_json(result.stdout)
        
        # Should have Cutter events section
        self.assertIn('recent_cutter_events', data)
        self.assertIn('count', data['recent_cutter_events'])
        self.assertIn('events', data['recent_cutter_events'])
        
        # Should find our test events
        self.assertGreaterEqual(
            data['recent_cutter_events']['count'],
            2,
            "Should find at least 2 Cutter events"
        )
    
    def test_weekly_ritual_output_to_file(self):
        """Weekly ritual should write to file when --output specified."""
        env = os.environ.copy()
        env['TEST_DB_PATH'] = self.test_db_path
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, 'scripts/weekly_ritual.py', '--output', output_file],
                capture_output=True,
                text=True,
                env=env,
                cwd=Path(__file__).parent.parent
            )
            
            self.assertEqual(result.returncode, 0)
            
            # File should exist and contain valid JSON
            self.assertTrue(os.path.exists(output_file))
            
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            self.assertIn('ritual', data)
            self.assertIn('ds2_unowned_recognition', data)
            self.assertIn('ds5_deferred_recognition', data)
        
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def _extract_json(self, output: str):
        lines = [line for line in output.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            if line.lstrip().startswith(("{", "[")):
                try:
                    return json.loads("\n".join(lines[i:]))
                except json.JSONDecodeError:
                    continue
        raise json.JSONDecodeError("No JSON found", output, 0)
    
    def test_weekly_ritual_contains_no_advice(self):
        """Weekly ritual output should contain no advice or 'you should' statements."""
        env = os.environ.copy()
        env['TEST_DB_PATH'] = self.test_db_path
        
        result = subprocess.run(
            [sys.executable, 'scripts/weekly_ritual.py'],
            capture_output=True,
            text=True,
            env=env,
            cwd=Path(__file__).parent.parent
        )
        
        output_lower = result.stdout.lower()
        
        # Forbidden phrases (constitutional enforcement)
        forbidden_phrases = [
            'you should',
            'recommend',
            'suggestion',
            'please fix',
            'needs attention',
            'action required',
            'warning:',
            'alert:'
        ]
        
        for phrase in forbidden_phrases:
            self.assertNotIn(
                phrase,
                output_lower,
                f"Output should not contain advice phrase: '{phrase}'"
            )


if __name__ == '__main__':
    unittest.main()
