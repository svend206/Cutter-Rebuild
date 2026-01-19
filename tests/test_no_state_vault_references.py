"""
Test: Verify No "State Vault" References Remain

This test ensures the universal rename from "State Vault" to "State Ledger"
is complete across the entire repository.

REQUIREMENT: Zero occurrences of "State Vault" allowed anywhere.
"""

import os
import sys
from pathlib import Path


# Directories to exclude from search
EXCLUDE_DIRS = {
    '.git',
    '__pycache__',
    'node_modules',
    '.cursor',
    'venv',
    'env',
    '.venv',
    '_archive',  # Historical records
    'Archive'  # Historical records
}

# File extensions to check
TEXT_EXTENSIONS = {
    '.py', '.md', '.txt', '.json', '.yaml', '.yml',
    '.js', '.ts', '.html', '.css', '.sql', '.sh',
    '.bat', '.ps1', '.rst', '.toml', '.ini', '.cfg'
}


def should_check_file(file_path: Path) -> bool:
    """Determine if file should be checked for State Ledger references."""
    
    # Skip this test file itself
    if file_path.name == 'test_no_state_vault_references.py':
        return False
    
    # Skip if in excluded directory
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False
    
    # Skip binary files
    if file_path.suffix.lower() in {'.db', '.pyc', '.pyo', '.so', '.dll', '.exe', '.bin', '.backup'}:
        return False
    
    # Check text files
    if file_path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    
    # Check files without extension (e.g., shell scripts)
    if not file_path.suffix and file_path.is_file():
        return True
    
    return False


def find_state_vault_references(root_dir: Path = Path(".")):
    """
    Search for any remaining "State Vault" references.
    
    Returns:
        List of tuples: (file_path, line_number, line_content)
    """
    violations = []
    
    for file_path in root_dir.rglob("*"):
        if not file_path.is_file():
            continue
        
        if not should_check_file(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, start=1):
                    if 'State Vault' in line:
                        violations.append((
                            str(file_path),
                            line_num,
                            line.strip()[:100]  # Truncate long lines
                        ))
        except Exception as e:
            # Skip files that can't be read
            print(f"  Warning: Could not read {file_path}: {e}", file=sys.stderr)
            continue
    
    return violations


def test_no_state_vault_references():
    """Test that no 'State Vault' references exist in the repository."""
    print("\n" + "=" * 80)
    print("TEST: No 'State Vault' References Remain")
    print("=" * 80)
    
    print("\nScanning repository for 'State Vault' references...")
    
    violations = find_state_vault_references()
    
    if violations:
        print(f"\n[FAIL] Found {len(violations)} 'State Vault' reference(s):")
        print()
        
        for file_path, line_num, line_content in violations:
            # Handle Unicode characters in output
            try:
                # Convert to ASCII-safe representation
                safe_path = file_path.encode('ascii', 'replace').decode('ascii')
                safe_content = line_content.encode('ascii', 'replace').decode('ascii')
                print(f"  {safe_path}:{line_num}")
                print(f"    {safe_content}")
            except Exception:
                print(f"  [file with special chars]:{line_num}")
                print(f"    [content contains special characters]")
            print()
        
        print("=" * 80)
        print(f"[FAIL] Universal rename incomplete: {len(violations)} violation(s)")
        print("=" * 80)
        return False
    
    else:
        print("\n[PASS] No 'State Vault' references found")
        print("=" * 80)
        print("[SUCCESS] Universal rename complete")
        print("=" * 80)
        return True


if __name__ == '__main__':
    success = test_no_state_vault_references()
    sys.exit(0 if success else 1)
