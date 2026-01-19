"""
State Ledger: Append-Only Ledger of Explicit Recognition

This module provides the ONLY authorized write path into the State Ledger.
All state declarations must pass through this boundary.

Constitutional Authority:
- DS-2 (Unowned Recognition): No committee recognition, single owner enforcement
- DS-5 (Deferred Recognition): Cadence tracking for recognition gaps
- C4 (Irreversible Memory): Append-only, no edits/deletes
- C5 (Separation of Observation and Judgment): No interpretation, only declaration

Critical Invariants:
- Explicit recognition only (no auto-generation, no inference)
- No silent continuity (no carry-forward, no defaults)
- No explanation fields (no "why")
- Recognition owner required (refuses if unowned)
"""

from .boundary import emit_state_declaration, get_current_owner, assign_owner, register_entity

__all__ = ['emit_state_declaration', 'get_current_owner', 'assign_owner', 'register_entity']
