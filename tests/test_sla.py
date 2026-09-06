from datetime import datetime, timedelta, timezone

import pytest
from django.contrib.auth import get_user_model

from tickets.models import Ticket
from tickets.sla import deadline_for, overdue_tickets


def test_priority_deadlines_are_deterministic() -> None:
    opened = datetime(2026, 4, 1, 9, tzinfo=timezone.utc)
    assert deadline_for(Ticket.Priority.EMERGENCY, opened) == opened + timedelta(hours=2)
    assert deadline_for(Ticket.Priority.HIGH, opened) == opened + timedelta(hours=24)
    assert deadline_for(Ticket.Priority.NORMAL, opened) == opened + timedelta(hours=72)
    assert deadline_for(Ticket.Priority.LOW, opened) == opened + timedelta(days=7)


@pytest.mark.django_db
def test_overdue_query_excludes_resolved_and_closed_tickets() -> None:
    user = get_user_model().objects.create_user(username="reporter")
    past = datetime(2026, 4, 1, 9, tzinfo=timezone.utc)
    active = Ticket.objects.create(title="Active", description="", reported_by=user, due_at=past)
    Ticket.objects.create(title="Resolved", description="", reported_by=user, due_at=past, status=Ticket.Status.RESOLVED)
    assert list(overdue_tickets(datetime(2026, 4, 2, 9, tzinfo=timezone.utc))) == [active]
