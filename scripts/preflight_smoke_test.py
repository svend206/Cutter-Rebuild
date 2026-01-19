#!/usr/bin/env python3
"""
Smoke test for DB mode guard + preflight checks.
Case A (PROD): TEST_DB_PATH unset => database import succeeds.
Case B (Misconfigured TEST): TEST_DB_PATH points to prod path => import fails.
Case C (TEST): TEST_DB_PATH points to a valid test path => import succeeds,
               ops-only schema fails preflight, reset_db schema passes.
"""
import os
import sys
import time
import tempfile
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import importlib
import database
from ops_layer import preflight


def new_temp_db() -> Path:
    ts = int(time.time() * 1000)
    return Path(tempfile.gettempdir()) / f"preflight_smoke_test_{ts}.db"


def run_import_check(env_overrides: dict) -> int:
    env = os.environ.copy()
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-c", "import database"],
        env=env,
        capture_output=True,
        text=True,
    ).returncode


def main() -> int:
    # Case A: PROD mode passes when TEST_DB_PATH is unset
    rc = run_import_check({"TEST_DB_PATH": ""})
    if rc != 0:
        print("[FAIL] PROD mode import failed with TEST_DB_PATH unset")
        return 1
    print("[OK] PROD mode import passed (TEST_DB_PATH unset)")

    # Case B: Misconfigured TEST_DB_PATH fails loudly (prod path)
    rc = run_import_check({"TEST_DB_PATH": str(ROOT / "cutter.db")})
    if rc == 0:
        print("[FAIL] Misconfigured TEST_DB_PATH unexpectedly passed")
        return 1
    print("[OK] Misconfigured TEST_DB_PATH failed as expected")

    # Case C: Correct TEST_DB_PATH passes and preflight behaves
    db_path = new_temp_db()
    if db_path.exists():
        db_path.unlink()

    os.environ["TEST_DB_PATH"] = str(db_path)
    importlib.reload(database)

    # Create ops tables only
    database.initialize_database()
    missing = preflight.check_preflight(db_path)
    if not missing:
        print("[FAIL] Preflight unexpectedly passed with ops-only schema")
        return 1
    print("[OK] Preflight failed as expected with ops-only schema")

    # Create full schema via reset_db
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "reset_db.py"), "--db-path", str(db_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("[FAIL] reset_db.py failed")
        print(result.stdout)
        print(result.stderr)
        return 1

    missing = preflight.check_preflight(db_path)
    if missing:
        print("[FAIL] Preflight did not pass after reset_db")
        for item in missing:
            print(f"  - {item}")
        return 1

    print("[OK] Preflight passed after reset_db")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
