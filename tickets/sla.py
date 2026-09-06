from datetime import datetime, timedelta

from django.db.models import QuerySet
from django.utils import timezone

from tickets.models import Ticket

SLA_BY_PRIORITY = {
    Ticket.Priority.LOW: timedelta(days=7),
    Ticket.Priority.NORMAL: timedelta(hours=72),
    Ticket.Priority.HIGH: timedelta(hours=24),
    Ticket.Priority.EMERGENCY: timedelta(hours=2),
}


def deadline_for(priority: str, opened_at: datetime | None = None) -> datetime:
    try:
        duration = SLA_BY_PRIORITY[priority]
    except KeyError as error:
        raise ValueError(f"unsupported priority: {priority}") from error
    return (opened_at or timezone.now()) + duration


def overdue_tickets(at: datetime | None = None) -> QuerySet[Ticket]:
    current_time = at or timezone.now()
    return Ticket.objects.filter(due_at__lt=current_time).exclude(status__in=(Ticket.Status.RESOLVED, Ticket.Status.CLOSED))
