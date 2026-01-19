"""
Ops-layer event emission helpers (read-only logic + Cutter Ledger write path).
"""

from typing import Optional, Dict, Any

from cutter_ledger.boundary import emit_cutter_event
from .stage_expectations import STAGE_EXPECTATION_SECONDS


def emit_carrier_handoff(
    subject_ref: str,
    carrier: Optional[str] = None,
    event_data: Optional[Dict[str, Any]] = None
) -> int:
    """
    Emit the factual event 'carrier_handoff' to the Cutter Ledger.
    """
    if not subject_ref:
        raise ValueError("subject_ref is required")

    payload: Optional[Dict[str, Any]] = None
    if event_data:
        payload = dict(event_data)
    if carrier is not None:
        if payload is None:
            payload = {}
        payload["carrier"] = carrier

    return emit_cutter_event(
        event_type="carrier_handoff",
        subject_ref=subject_ref,
        event_data=payload
    )


def emit_stage_started(subject_ref: str, stage: str) -> int:
    if not subject_ref:
        raise ValueError("subject_ref is required")
    if stage not in STAGE_EXPECTATION_SECONDS:
        raise ValueError(f"Unsupported stage: {stage}")

    return emit_cutter_event(
        event_type="stage_started",
        subject_ref=subject_ref,
        event_data={"stage": stage}
    )


def emit_stage_completed(subject_ref: str, stage: str) -> int:
    if not subject_ref:
        raise ValueError("subject_ref is required")
    if stage not in STAGE_EXPECTATION_SECONDS:
        raise ValueError(f"Unsupported stage: {stage}")

    return emit_cutter_event(
        event_type="stage_completed",
        subject_ref=subject_ref,
        event_data={"stage": stage}
    )
