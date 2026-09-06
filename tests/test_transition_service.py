import pytest
from django.contrib.auth import get_user_model

from tickets.models import Ticket
from tickets.workflow import InvalidTransition, transition_ticket


@pytest.mark.django_db
def test_transition_assigns_ticket_and_records_actor() -> None:
    users = get_user_model()
    reporter = users.objects.create_user(username="reporter")
    technician = users.objects.create_user(username="technician")
    ticket = Ticket.objects.create(title="Leaking pipe", description="Leak in room 2", reported_by=reporter)

    updated = transition_ticket(
        ticket_id=ticket.id,
        target=Ticket.Status.ASSIGNED,
        actor=reporter,
        assigned_to=technician,
        note="Dispatching nearby technician",
    )

    assert updated.assigned_to == technician
    event = updated.events.get()
    assert (event.from_status, event.to_status) == (Ticket.Status.OPEN, Ticket.Status.ASSIGNED)
    assert event.actor == reporter


@pytest.mark.django_db
def test_transition_requires_active_assignee() -> None:
    users = get_user_model()
    reporter = users.objects.create_user(username="reporter")
    inactive = users.objects.create_user(username="inactive", is_active=False)
    ticket = Ticket.objects.create(title="Broken light", description="Dark corridor", reported_by=reporter)

    with pytest.raises(InvalidTransition, match="active assignee"):
        transition_ticket(ticket_id=ticket.id, target=Ticket.Status.ASSIGNED, actor=reporter, assigned_to=inactive)
    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.OPEN
    assert not ticket.events.exists()


@pytest.mark.django_db
def test_resolution_and_closure_set_lifecycle_timestamps() -> None:
    users = get_user_model()
    actor = users.objects.create_user(username="technician")
    ticket = Ticket.objects.create(
        title="Service elevator",
        description="Routine service",
        reported_by=actor,
        assigned_to=actor,
        status=Ticket.Status.IN_PROGRESS,
    )
    resolved = transition_ticket(ticket_id=ticket.id, target=Ticket.Status.RESOLVED, actor=actor)
    assert resolved.resolved_at is not None
    closed = transition_ticket(ticket_id=ticket.id, target=Ticket.Status.CLOSED, actor=actor)
    assert closed.closed_at is not None
