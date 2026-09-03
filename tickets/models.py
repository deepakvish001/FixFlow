from django.conf import settings
from django.db import models


class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        EMERGENCY = "emergency", "Emergency"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=160)
    description = models.TextField()
    priority = models.CharField(max_length=16, choices=Priority, default=Priority.NORMAL)
    status = models.CharField(max_length=16, choices=Status, default=Status.OPEN)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"#{self.pk}: {self.title}"
