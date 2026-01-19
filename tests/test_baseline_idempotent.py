"""
Test: Baseline Declarations Script is Idempotent

Constitutional enforcement: Baseline script must refuse to emit duplicate
declarations. Duplicates create noise and undermine meaning.
"""

import unittest
import subprocess
import sys
import os
import tempfile
import sqlite3
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ensure TEST_DB_PATH is set before importing database
if not os.environ.get("TEST_DB_PATH"):
    bootstrap_path = Path(tempfile.gettempdir()) / "test_baseline_idempotent_bootstrap.db"
    os.environ["TEST_DB_PATH"] = str(bootstrap_path)

import database
from state_ledger import boundary


class TestBaselineIdempotent(unittest.TestCase):
    """Test that baseline_declarations.py is idempotent and refuses duplicates."""
    
    def setUp(self):
        """Set up temporary database."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.test_dir) / "test.db"
        
        # Set TEST_DB_PATH environment variable
        os.environ['TEST_DB_PATH'] = str(self.test_db_path)
        
        # Initialize database with full schema
        self._initialize_test_database()
    
    def tearDown(self):
        """Clean up temporary directory."""
        # Remove TEST_DB_PATH
        if 'TEST_DB_PATH' in os.environ:
            del os.environ['TEST_DB_PATH']
        
        import shutil
        if Path(self.test_dir).exists():
            try:
                shutil.rmtree(self.test_dir)
            except Exception as e:
                print(f"Warning: Could not clean up test directory: {e}")
    
    def _initialize_test_database(self):
        """Initialize test database with State Ledger schema."""
        # Run reset_db.py to get full schema
        result = subprocess.run(
            [sys.executable, 'scripts/reset_db.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        if result.returncode != 0:
            self.fail(f"Failed to initialize test database: {result.stderr}")
    
    def test_baseline_runs_successfully_first_time(self):
        """First run of baseline script should succeed."""
        # Run bootstrap to create entities
        result = subprocess.run(
            [sys.executable, 'scripts/bootstrap_initial_registry.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        self.assertEqual(result.returncode, 0, f"Bootstrap failed: {result.stderr}")
        
        # Run baseline (first time)
        result = subprocess.run(
            [sys.executable, 'scripts/baseline_declarations.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        self.assertEqual(result.returncode, 0, f"First baseline run should succeed: {result.stderr}")
        
        # Verify valid JSON output
        import json
        output = json.loads(result.stdout)
        self.assertIn('baseline_declarations', output)
        self.assertGreater(len(output['baseline_declarations']), 0, "Should create baseline declarations")
        self.assertEqual(len(output.get('errors', [])), 0, "Should have no errors")
    
    def test_baseline_refuses_second_run(self):
        """Second run of baseline script should refuse (idempotency)."""
        # Run bootstrap to create entities
        subprocess.run(
            [sys.executable, 'scripts/bootstrap_initial_registry.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        # Run baseline (first time)
        result1 = subprocess.run(
            [sys.executable, 'scripts/baseline_declarations.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        self.assertEqual(result1.returncode, 0, "First run should succeed")
        
        # Run baseline (second time - should refuse)
        result2 = subprocess.run(
            [sys.executable, 'scripts/baseline_declarations.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        # Should exit with error
        self.assertNotEqual(result2.returncode, 0, "Second run should fail/refuse")
        
        # Should mention refusal reason
        self.assertIn("Baseline already exists", result2.stderr, "Should mention existing baseline")
        self.assertIn("Refusing", result2.stderr, "Should explicitly refuse")
        self.assertIn("duplicate", result2.stderr.lower(), "Should mention duplicates")
    
    def test_baseline_force_flag_allows_duplicates(self):
        """Baseline script with --force flag should allow duplicates."""
        # Run bootstrap to create entities
        subprocess.run(
            [sys.executable, 'scripts/bootstrap_initial_registry.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        # Run baseline (first time)
        result1 = subprocess.run(
            [sys.executable, 'scripts/baseline_declarations.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        self.assertEqual(result1.returncode, 0, "First run should succeed")
        
        import json
        output1 = json.loads(result1.stdout)
        first_count = len(output1['baseline_declarations'])
        
        # Run baseline with --force flag
        result2 = subprocess.run(
            [sys.executable, 'scripts/baseline_declarations.py', 
             '--force', 'I_UNDERSTAND_DUPLICATES_CREATE_NOISE'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        # Should succeed with force flag
        self.assertEqual(result2.returncode, 0, f"Force run should succeed: {result2.stderr}")
        
        # Verify warning about force mode
        self.assertIn("FORCE MODE ENABLED", result2.stderr, "Should warn about force mode")
        
        # Verify declarations were created
        output2 = json.loads(result2.stdout)
        second_count = len(output2['baseline_declarations'])
        self.assertEqual(second_count, first_count, "Should create same number of declarations")
        
        # Verify total declarations in DB (should be 2x now)
        conn = sqlite3.connect(str(self.test_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM state__declarations")
        total_count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(total_count, first_count * 2, "Should have duplicate declarations in DB")
    
    def test_baseline_force_flag_requires_exact_confirmation(self):
        """Baseline --force flag must have exact confirmation string."""
        # Run bootstrap to create entities
        subprocess.run(
            [sys.executable, 'scripts/bootstrap_initial_registry.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        # Run baseline with wrong confirmation string
        result = subprocess.run(
            [sys.executable, 'scripts/baseline_declarations.py', 
             '--force', 'YES'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        # Should fail
        self.assertNotEqual(result.returncode, 0, "Wrong confirmation should fail")
        self.assertIn("Invalid force confirmation", result.stderr, "Should mention invalid confirmation")
    
    def test_baseline_refusal_lists_conflicting_entities(self):
        """Baseline refusal should list which entities already have baselines."""
        # Run bootstrap to create entities
        subprocess.run(
            [sys.executable, 'scripts/bootstrap_initial_registry.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        # Run baseline (first time)
        subprocess.run(
            [sys.executable, 'scripts/baseline_declarations.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        # Run baseline (second time - should refuse with details)
        result = subprocess.run(
            [sys.executable, 'scripts/baseline_declarations.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=os.environ,
            timeout=30
        )
        
        # Should have refused list in output
        import json
        output = json.loads(result.stderr)
        self.assertIn('refused', output, "Output should have 'refused' list")
        self.assertGreater(len(output['refused']), 0, "Should list refused entities")
        
        # Check first refused entity has required fields
        first_refused = output['refused'][0]
        self.assertIn('entity_ref', first_refused)
        self.assertIn('scope_ref', first_refused)
        self.assertIn('reason', first_refused)


if __name__ == '__main__':
    unittest.main()
