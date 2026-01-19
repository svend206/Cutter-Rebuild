"""
Cutter Ledger: Industry-Agnostic Epistemic Ledger

This module provides the ONLY authorized write path into the Cutter Ledger.
All operational exhaust must pass through this boundary.

Constitutional Authority:
- C1 (Outcome Agnosticism): No evaluative language
- C4 (Irreversible Memory): Append-only, no edits/deletes
- C7 (Overrides Must Leave Scars): Preserve magnitude, frequency, persistence

Provenance Design:
- Deterministic: service_id + version (not stack inspection)
- Debug callsite: Optional best-effort in event_data.debug.callsite
"""

from .boundary import emit_cutter_event, get_events

__all__ = ['emit_cutter_event', 'get_events']
