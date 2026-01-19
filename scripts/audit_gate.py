"""
Audit gate for Conformance & Craft thresholds.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Tuple


WATCHED_DIRS = [
    "ops_layer/",
    "cutter_ledger/",
    "state_ledger/",
    "scripts/",
    "migrations/",
]


def _run_git(args: List[str]) -> Tuple[int, str, str]:
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _get_latest_audit_tag() -> Optional[str]:
    code, out, _ = _run_git([
        "for-each-ref",
        "--sort=-creatordate",
        "--format=%(refname:short)",
        "refs/tags/audit-*",
        "refs/tags/conformance-*",
    ])
    if code != 0 or not out:
        return None
    return out.splitlines()[0].strip()


def _get_initial_commit() -> Optional[str]:
    code, out, _ = _run_git(["rev-list", "--max-parents=0", "HEAD"])
    if code != 0 or not out:
        return None
    return out.splitlines()[0].strip()


def _get_changed_files(since_ref: str) -> List[str]:
    code, out, _ = _run_git(["diff", "--name-only", f"{since_ref}..HEAD"])
    if code != 0:
        return []
    return [line for line in out.splitlines() if line.strip()]


def _get_loc_delta(since_ref: str) -> int:
    code, out, _ = _run_git(["diff", "--numstat", f"{since_ref}..HEAD"])
    if code != 0 or not out:
        return 0
    total = 0
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        added, deleted = parts[0], parts[1]
        added_val = int(added) if added.isdigit() else 0
        deleted_val = int(deleted) if deleted.isdigit() else 0
        total += added_val + deleted_val
    return total


def _has_changes_in_dir(files: List[str], prefix: str) -> bool:
    return any(path.startswith(prefix) for path in files)


def _parse_iso_ts(value: str) -> Optional[datetime]:
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _load_override_token() -> Optional[dict]:
    token_path = Path("reports") / "audit_override.json"
    if not token_path.exists():
        return None
    try:
        payload = json.loads(token_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _validate_override_token(payload: dict) -> Optional[dict]:
    scope = payload.get("scope")
    reason = payload.get("reason")
    created_by = payload.get("created_by")
    created_at = payload.get("created_at")
    expires_at = payload.get("expires_at")

    if scope not in {"docs-only", "remediation-only"}:
        return None
    if not isinstance(reason, str) or not reason.strip():
        return None
    if not isinstance(created_by, str) or not created_by.strip():
        return None
    if not isinstance(created_at, str) or not isinstance(expires_at, str):
        return None

    created_dt = _parse_iso_ts(created_at)
    expires_dt = _parse_iso_ts(expires_at)
    if created_dt is None or expires_dt is None:
        return None
    if created_dt.tzinfo is None:
        created_dt = created_dt.replace(tzinfo=timezone.utc)
    if expires_dt.tzinfo is None:
        expires_dt = expires_dt.replace(tzinfo=timezone.utc)

    if expires_dt > created_dt + timedelta(hours=4):
        return None
    if datetime.now(timezone.utc) > expires_dt:
        return None
    return {
        "scope": scope,
        "expires_at": expires_at,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Conformance & Craft audit gate.")
    parser.add_argument("--since", dest="since", default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    latest_tag = _get_latest_audit_tag()
    since_ref = args.since or latest_tag
    reasons: List[str] = []

    if since_ref is None:
        reasons.append("AUDIT REQUIRED: no audit tag found")
        since_ref = _get_initial_commit() or "HEAD"

    changed_files = _get_changed_files(since_ref)
    loc_delta = _get_loc_delta(since_ref)

    non_canon_files = [f for f in changed_files if not f.startswith("canon/")]
    canon_changed = _has_changes_in_dir(changed_files, "canon/")

    if loc_delta > 500:
        reasons.append(f"AUDIT REQUIRED: LOC delta {loc_delta} > 500")
    if len(non_canon_files) >= 10:
        reasons.append(
            f"AUDIT REQUIRED: {len(non_canon_files)} files changed outside canon >= 10"
        )
    for watched in WATCHED_DIRS:
        if _has_changes_in_dir(changed_files, watched):
            reasons.append(f"AUDIT REQUIRED: changes detected under {watched}")
    if canon_changed:
        reasons.append(
            "AUDIT REQUIRED: canon/ changed; verify code conforms to updated canon"
        )

    print("Conformance & Craft Audit Gate")
    print(f"Since: {since_ref}")
    if latest_tag:
        print(f"Last audit tag: {latest_tag}")
    else:
        print("Last audit tag: none")
    print(f"LOC delta: {loc_delta}")
    print(f"Files changed (non-canon): {len(non_canon_files)}")

    if args.verbose:
        if changed_files:
            print("Changed files:")
            for path in changed_files:
                print(f"- {path}")
        else:
            print("Changed files: none")

    if reasons:
        payload = _load_override_token()
        token = _validate_override_token(payload) if payload else None
        if token:
            print(
                f"AUDIT OVERRIDE ACTIVE: {token['scope']} (expires {token['expires_at']})"
            )
            return 0
        for line in reasons:
            print(line)
        return 2

    print("OK: audit not required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
