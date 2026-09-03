from tickets.workflow import can_transition


def test_ticket_can_move_from_open_to_assigned() -> None:
    assert can_transition("open", "assigned") is True


def test_closed_ticket_cannot_be_reopened_directly() -> None:
    assert can_transition("closed", "open") is False
