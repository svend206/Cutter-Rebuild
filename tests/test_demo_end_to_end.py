"""
Test End-to-End Demo Script

Smoke test that verifies the demo script runs successfully.
"""

import unittest
import subprocess
import sys
import os
import tempfile
from pathlib import Path


class TestDemoEndToEnd(unittest.TestCase):
    """Smoke test for end-to-end demo script."""
    
    def test_demo_runs_successfully(self):
        """Demo script should run and exit with code 0."""
        # Create unique temp database for this test
        temp_dir = tempfile.gettempdir()
        import time
        timestamp = int(time.time() * 1000)
        test_db = Path(temp_dir) / f"test_demo_e2e_{timestamp}.db"
        
        # Clean up if exists
        if test_db.exists():
            test_db.unlink()
        
        # Set up environment
        env = os.environ.copy()
        env["TEST_DB_PATH"] = str(test_db)
        
        # Run demo script
        demo_script = Path(__file__).parent.parent / "scripts" / "demo_end_to_end.py"
        
        result = subprocess.run(
            [sys.executable, str(demo_script)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )
        
        # Print output for debugging if failed
        if result.returncode != 0:
            print("=== STDOUT ===", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            print("=== STDERR ===", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        
        # Verify success
        self.assertEqual(
            result.returncode, 0,
            f"Demo script failed with exit code {result.returncode}"
        )
        
        # Verify key phrases in output (smoke test only)
        stdout_lower = result.stdout.lower()
        self.assertIn("phase 1", stdout_lower, "Should show Phase 1 (Ops → Cutter)")
        self.assertIn("phase 2", stdout_lower, "Should show Phase 2 (State Ledger)")
        self.assertIn("phase 3", stdout_lower, "Should show Phase 3 (Queries)")
        self.assertIn("demo complete", stdout_lower, "Should show completion message")
        
        # Verify Cutter Ledger events were emitted
        self.assertIn("cutter ledger", stdout_lower, "Should mention Cutter Ledger")
        self.assertIn("event captured", stdout_lower, "Should capture events")
        
        # Verify State Ledger operations
        self.assertIn("state ledger", stdout_lower, "Should mention State Ledger")
        self.assertIn("entity registered", stdout_lower, "Should register entity")
        self.assertIn("owner assigned", stdout_lower, "Should assign owner")
        self.assertIn("reclassification", stdout_lower, "Should emit RECLASSIFICATION")
        self.assertIn("reaffirmation", stdout_lower, "Should emit REAFFIRMATION")
        
        # Verify queries executed
        self.assertIn("query", stdout_lower, "Should execute queries")
        self.assertIn("ds-1", stdout_lower, "Should query DS-1")
        self.assertIn("ds-2", stdout_lower, "Should query DS-2")
        self.assertIn("ds-5", stdout_lower, "Should query DS-5")
        
        # Clean up test database
        try:
            if test_db.exists():
                test_db.unlink()
        except PermissionError:
            # Windows file locking can be stubborn, just pass
            pass
    
    def test_demo_produces_json_output(self):
        """Demo script should output valid JSON for queries."""
        temp_dir = tempfile.gettempdir()
        import time
        timestamp = int(time.time() * 1000)
        test_db = Path(temp_dir) / f"test_demo_e2e_json_{timestamp}.db"
        
        if test_db.exists():
            test_db.unlink()
        
        env = os.environ.copy()
        env["TEST_DB_PATH"] = str(test_db)
        
        demo_script = Path(__file__).parent.parent / "scripts" / "demo_end_to_end.py"
        
        result = subprocess.run(
            [sys.executable, str(demo_script)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )
        
        self.assertEqual(result.returncode, 0, "Demo should succeed")
        
        # Check for JSON-like structures in output
        stdout = result.stdout
        
        # Should have JSON arrays or objects
        self.assertIn("[", stdout, "Should contain JSON arrays")
        self.assertIn("{", stdout, "Should contain JSON objects")
        self.assertIn('"entity_ref"', stdout, "Should have entity_ref fields")
        self.assertIn('"declaration_id"', stdout, "Should have declaration_id fields")
        
        # Clean up
        try:
            if test_db.exists():
                test_db.unlink()
        except PermissionError:
            pass


if __name__ == '__main__':
    unittest.main()
