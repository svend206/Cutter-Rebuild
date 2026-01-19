"""
Ops-only expectations for Loop 1 stages (seconds).
"""

from typing import Dict

STAGE_EXPECTATION_SECONDS: Dict[str, int] = {
    "machining": 3600,
    "inspection": 1800,
    "packing": 900,
}


def get_expected_duration_seconds(stage: str) -> int:
    if stage not in STAGE_EXPECTATION_SECONDS:
        raise ValueError(f"Unsupported stage: {stage}")
    return STAGE_EXPECTATION_SECONDS[stage]
