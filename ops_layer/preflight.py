"""
Preflight checks for required ledger schema and append-only triggers.
Fail-fast before serving when schema is incomplete.
"""
import os
import re
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional

import database


REQUIRED_TABLES = [
    "ops__materials",
    "ops__shop_config",
    "ops__quote_history",
    "ops__customers",
    "ops__contacts",
    "ops__parts",
    "ops__quotes",
    "ops__quote_outcome_events",
    "ops__custom_tags",
    "cutter__events",
    "state__declarations",
]

REQUIRED_TRIGGERS = [
    ("cutter__events", "UPDATE"),
    ("cutter__events", "DELETE"),
    ("state__declarations", "UPDATE"),
    ("state__declarations", "DELETE"),
]


def _get_db_path(db_path: Optional[Path] = None) -> Path:
    if db_path is not None:
        return Path(db_path)
    return database.DB_PATH


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cur.fetchone() is not None


def _has_before_trigger(conn: sqlite3.Connection, table_name: str, operation: str) -> bool:
    cur = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='trigger' AND tbl_name=?",
        (table_name,),
    )
    table_upper = table_name.upper()
    op_upper = operation.upper()
    for (sql,) in cur.fetchall():
        if not sql:
            continue
        sql_upper = sql.upper()
        if f"BEFORE {op_upper}" in sql_upper and table_upper in sql_upper:
            return True
    return False


def _lint_direct_sql_bypass() -> List[str]:
    repo_root = Path(__file__).parent.parent
    targets = [repo_root / "scripts", repo_root / "tests"]
    allow_marker = "# CUTTER: LEDGER_SQL_ALLOWED (BOOTSTRAP)"
    table_pattern = re.compile(r"\b(cutter__events|state__declarations)\b", re.IGNORECASE)
    write_patterns = [
        re.compile(r"\bINSERT\s+INTO\s+(cutter__events|state__declarations)\b", re.IGNORECASE),
        re.compile(r"\bUPDATE\s+(cutter__events|state__declarations)\b", re.IGNORECASE),
        re.compile(r"\bDELETE\s+FROM\s+(cutter__events|state__declarations)\b", re.IGNORECASE),
    ]
    drop_trigger_pattern = re.compile(r"\bDROP\s+TRIGGER\b", re.IGNORECASE)
    flagged: List[str] = []
    for root in targets:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            content = path.read_text(encoding="utf-8", errors="ignore")
            if allow_marker in content:
                continue
            has_write = any(pattern.search(content) for pattern in write_patterns)
            if drop_trigger_pattern.search(content) and table_pattern.search(content):
                has_write = True
            if not has_write:
                continue
            if "require_test_db(" not in content:
                flagged.append(str(path.relative_to(repo_root)))
    return sorted(set(flagged))


def check_preflight(db_path: Optional[Path] = None) -> List[str]:
    db_path = _get_db_path(db_path)
    missing: List[str] = []
    conn = sqlite3.connect(db_path)
    try:
        for table in REQUIRED_TABLES:
            if not _table_exists(conn, table):
                missing.append(f"table:{table}")
        for table_name, operation in REQUIRED_TRIGGERS:
            if not _has_before_trigger(conn, table_name, operation):
                missing.append(f"trigger:{table_name}:{operation.lower()}")
    finally:
        conn.close()
    return missing


def run_preflight_or_exit(db_path: Optional[Path] = None) -> None:
    missing = check_preflight(db_path)
    lint_hits = _lint_direct_sql_bypass()
    if not missing:
        if not lint_hits:
            return
    if lint_hits:
        print("\n[BOOTSTRAP ERROR] Direct SQL ledger writes without test guard:")
        for item in lint_hits:
            print(f"  - {item}")
        print("\nRecommended fixes:")
        print("  - Add database.require_test_db(...) to the file entrypoint")
        raise SystemExit(1)
    print("\n[BOOTSTRAP ERROR] Missing required database objects:")
    for item in missing:
        print(f"  - {item}")
    print("\nRecommended fixes:")
    print("  - python scripts/reset_db.py")
    print("  - or run required migrations in ./migrations (manual)")
    raise SystemExit(1)
