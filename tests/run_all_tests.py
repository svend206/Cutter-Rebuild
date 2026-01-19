"""
Master Test Runner - Comprehensive Testing Suite
Phase 5.5 Validation

Runs all tests in order:
1. Unit Tests (Genesis Hash)
2. Seed Test Data (Pattern Matching)
3. Integration Tests (End-to-End)
4. Validation Report

Usage:
    python tests/run_all_tests.py
    python tests/run_all_tests.py --skip-seed (if data already seeded)
    python tests/run_all_tests.py --clean (removes test data after)
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def run_command(command, cwd=None, env=None):
    """Run a command and return success status"""
    try:
        # Merge custom environment with current environment
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
        
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True,
            env=run_env
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Error running command: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Run all test suites')
    parser.add_argument('--skip-seed', action='store_true', help='Skip seeding test data')
    parser.add_argument('--clean', action='store_true', help='Clean test data after tests')
    parser.add_argument('--unit-only', action='store_true', help='Run only unit tests')
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    test_results = {
        'naming_check': None,
        'unit_tests': None,
        'data_seeding': None,
        'integration_tests': None
    }
    
    start_time = datetime.now()
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP -1: Setup Isolated Test Database (Hermetic Testing)
    # ═══════════════════════════════════════════════════════════════════
    
    print("\n" + "="*70)
    print("  STEP -1: TEST DATABASE SETUP - Hermetic Environment")
    print("="*70 + "\n")
    
    print("Creating isolated test database to prevent data pollution...\n")
    
    # Set up test database and configure environment
    import tempfile
    test_db_path = Path(tempfile.gettempdir()) / "cutter_test.db"
    test_env = {"TEST_DB_PATH": str(test_db_path)}
    
    # Create test database
    test_db_setup = run_command('python tests/test_setup.py', cwd=project_root, env=test_env)
    
    if not test_db_setup:
        print("\n[FAILED] Test database setup failed.")
        print("   Cannot proceed without isolated test environment.")
        return False
    
    # Set environment variable for this process and all subprocesses
    os.environ["TEST_DB_PATH"] = str(test_db_path)
    
    print("\n" + "="*70)
    print("  THE CUTTER - COMPREHENSIVE TEST SUITE")
    print("  Phase 5.5: Genesis Hash + Pattern Matching Validation")
    print("="*70)
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 0: Repository Naming Check (Constitutional Compliance)
    # ═══════════════════════════════════════════════════════════════════
    
    print_header("STEP 0: NAMING CHECK - State Ledger Convergence")
    print("Verifying zero legacy naming references remain in repository...\n")
    
    test_results['naming_check'] = run_command('python tests/test_no_state_vault_references.py', cwd=project_root, env=test_env)
    
    if not test_results['naming_check']:
        print("\n[FAILED] Naming check failed. Legacy name references found.")
        print("   Repository violates naming convergence requirement.")
        print("   Review violations above and update before continuing.")
        return False
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 1: Unit Tests (Genesis Hash)
    # ═══════════════════════════════════════════════════════════════════
    
    print_header("STEP 1: UNIT TESTS - Genesis Hash Logic")
    print("Testing determinism, uniqueness, parametric shapes, and edge cases...\n")
    
    test_results['unit_tests'] = run_command('python tests/test_genesis_hash.py', cwd=project_root, env=test_env)
    
    if not test_results['unit_tests']:
        print("\n[FAILED] Unit tests failed. Cannot proceed with integration tests.")
        print("   Fix Genesis Hash logic before continuing.")
        return False
    
    if args.unit_only:
        print("\n[SUCCESS] Unit tests complete. Exiting (--unit-only flag)")
        return True
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 2: Seed Test Data (Pattern Matching)
    # ═══════════════════════════════════════════════════════════════════
    
    if not args.skip_seed:
        print_header("STEP 2: SEED TEST DATA - Pattern Matching Scenarios")
        print("Creating realistic historical quotes for pattern detection...\n")
        
        test_results['data_seeding'] = run_command('python tests/seed_test_data.py --scenario all', cwd=project_root, env=test_env)
        
        if not test_results['data_seeding']:
            print("\n[WARNING] Data seeding failed, but we can continue with existing data.")
    else:
        print_header("STEP 2: SEED TEST DATA - SKIPPED")
        print("Using existing test data (--skip-seed flag)\n")
        test_results['data_seeding'] = True
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 3: Integration Tests (End-to-End)
    # ═══════════════════════════════════════════════════════════════════
    
    print_header("STEP 3: INTEGRATION TESTS - End-to-End Workflows")
    print("Testing File Mode, Napkin Mode, Pattern Matching API...\n")
    
    print("[WARNING] Integration tests require Flask server to be running.")
    print("   The test suite will attempt to start it automatically.\n")
    
    test_results['integration_tests'] = run_command('python tests/test_integration.py', cwd=project_root, env=test_env)
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 4: Clean Test Data (Optional)
    # ═══════════════════════════════════════════════════════════════════
    
    if args.clean:
        print_header("STEP 4: CLEANUP - Removing Test Data")
        print("Deleting all test quotes, parts, and customers...\n")
        
        run_command('python tests/seed_test_data.py --clean', cwd=project_root, env=test_env)
    
    # ═══════════════════════════════════════════════════════════════════
    # CLEANUP: Remove isolated test database
    # ═══════════════════════════════════════════════════════════════════
    
    if test_db_path.exists():
        try:
            test_db_path.unlink()
            print(f"\n[CLEANUP] Test database removed: {test_db_path}")
        except Exception as e:
            print(f"\n[WARNING] Could not remove test database: {e}")
    
    # ═══════════════════════════════════════════════════════════════════
    # FINAL REPORT
    # ═══════════════════════════════════════════════════════════════════
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*70)
    print("  FINAL TEST REPORT")
    print("="*70)
    
    def format_result(result):
        if result is None:
            return "[SKIP] SKIPPED"
        elif result:
            return "[PASS] PASSED"
        else:
            return "[FAIL] FAILED"
    
    print("  Naming Check (State Ledger):".ljust(50) + format_result(test_results['naming_check']))
    print("  Unit Tests (Genesis Hash):".ljust(50) + format_result(test_results['unit_tests']))
    print("  Data Seeding (Pattern Matching):".ljust(50) + format_result(test_results['data_seeding']))
    print("  Integration Tests (End-to-End):".ljust(50) + format_result(test_results['integration_tests']))
    
    print("="*70)
    
    all_passed = all(result for result in test_results.values() if result is not None)
    
    if all_passed:
        print("\n  [SUCCESS] ALL TESTS PASSED")
        print("  System is ready for production!\n")
    else:
        print("\n  [FAILED] SOME TESTS FAILED")
        print("  Review errors above before deploying.\n")
    
    print("="*70)
    print("  Total Duration:".ljust(50) + f"{duration:.1f} seconds")
    print("  Timestamp:".ljust(50) + end_time.strftime('%Y-%m-%d %H:%M:%S'))
    print("="*70 + "\n")
    
    # ═══════════════════════════════════════════════════════════════════
    # NEXT STEPS
    # ═══════════════════════════════════════════════════════════════════
    
    print("NEXT STEPS:")
    print("-" * 70)
    
    if all_passed:
        print("1. [OK] Naming convergence validated (State Ledger)")
        print("2. [OK] Genesis Hash generation is validated")
        print("3. [OK] Pattern matching data is seeded")
        print("4. [TEST] Manual Testing:")
        print("     - Start server: python app.py")
        print("     - Open http://localhost:5000")
        print("     - Test File Mode: Upload STL, verify Genesis Hash in console")
        print("     - Test Napkin Mode: Select Block 4x2x1, verify Genesis Hash")
        print("     - Test Pattern Matching: Create quote for TEST_SpaceX customer")
        print("5. [NEXT] Move to PDF Generation (Next Phase)")
    else:
        print("1. [ACTION] Fix failing tests before continuing")
        print("2. [REVIEW] Review error messages above")
        print("3. [RERUN] Re-run tests after fixes:")
        print("     python tests/run_all_tests.py --skip-seed")
    
    print("-" * 70 + "\n")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

