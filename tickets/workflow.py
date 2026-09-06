from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from tickets.models import Ticket, TicketEvent

ALLOWED_TRANSITIONS = {
    "open": {"assigned", "closed"},
    "assigned": {"in_progress", "open"},
    "in_progress": {"resolved", "assigned"},
    "resolved": {"closed", "in_progress"},
    "closed": set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


class InvalidTransition(ValueError):
    pass


@transaction.atomic
def transition_ticket(
    *,
    ticket_id: int,
    target: str,
    actor: get_user_model(),
    note: str = "",
    assigned_to: get_user_model() | None = None,
) -> Ticket:
    ticket = Ticket.objects.select_for_update().get(pk=ticket_id)
    current = ticket.status
    if not can_transition(current, target):
        raise InvalidTransition(f"ticket cannot move from {current} to {target}")
    if target == Ticket.Status.ASSIGNED:
        assignee = assigned_to or ticket.assigned_to
        if assignee is None or not assignee.is_active:
            raise InvalidTransition("an active assignee is required")
        ticket.assigned_to = assignee
    if target == Ticket.Status.OPEN:
        ticket.assigned_to = None
    now = timezone.now()
    if target == Ticket.Status.RESOLVED:
        ticket.resolved_at = now
    elif target == Ticket.Status.CLOSED:
        ticket.closed_at = now
    ticket.status = target
    ticket.save(update_fields=["status", "assigned_to", "resolved_at", "closed_at", "updated_at"])
    TicketEvent.objects.create(
        ticket=ticket,
        actor=actor,
        from_status=current,
        to_status=target,
        note=note.strip(),
    )
    return ticket
