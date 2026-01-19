"""
Install local git hooks for audit gating (opt-in).
"""

import os
import stat
from pathlib import Path


HOOK_CONTENT = """#!/bin/sh
python scripts/audit_gate.py
exit $?
"""


def main() -> int:
    repo_root = Path(__file__).parent.parent
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    pre_commit = hooks_dir / "pre-commit"
    pre_commit.write_text(HOOK_CONTENT, encoding="utf-8")

    try:
        mode = pre_commit.stat().st_mode
        pre_commit.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass

    print(f"Installed pre-commit hook at {pre_commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
