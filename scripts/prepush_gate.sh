#!/usr/bin/env bash
set -e

python scripts/audit_gate.py
python -m unittest
