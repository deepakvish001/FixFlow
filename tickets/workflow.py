ALLOWED_TRANSITIONS = {
    "open": {"assigned", "closed"},
    "assigned": {"in_progress", "open"},
    "in_progress": {"resolved", "assigned"},
    "resolved": {"closed", "in_progress"},
    "closed": set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())
