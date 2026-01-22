from typing import Optional

QUERY_CLASS_ALLOWED = "allowed"
QUERY_CLASS_REFUSE_BLAME = "refuse_blame"

QUERY_REGISTRY = {
    "blame.operator-score": QUERY_CLASS_REFUSE_BLAME,
    "blame.operator-rank": QUERY_CLASS_REFUSE_BLAME,
    "blame.operator-leaderboard": QUERY_CLASS_REFUSE_BLAME,
    "blame.operator-performance": QUERY_CLASS_REFUSE_BLAME,
    "blame.operator-latency-score": QUERY_CLASS_REFUSE_BLAME,
    "state.open-deadlines": QUERY_CLASS_ALLOWED,
    "state.open-response-deadlines": QUERY_CLASS_ALLOWED,
    "cutter.dwell-vs-expectation": QUERY_CLASS_ALLOWED,
}


def resolve_query_class(query_ref: str) -> Optional[str]:
    return QUERY_REGISTRY.get(query_ref)
