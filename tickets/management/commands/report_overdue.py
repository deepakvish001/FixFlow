import json

from django.core.management.base import BaseCommand

from tickets.sla import overdue_tickets


class Command(BaseCommand):
    help = "Report unresolved tickets past their SLA deadline"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--json", action="store_true", dest="as_json")

    def handle(self, *args, **options) -> None:
        tickets = list(overdue_tickets().order_by("due_at", "id").values("id", "title", "priority", "due_at"))
        if options["as_json"]:
            self.stdout.write(json.dumps(tickets, default=str))
            return
        for ticket in tickets:
            self.stdout.write(f"#{ticket['id']} [{ticket['priority']}] due {ticket['due_at']}: {ticket['title']}")
        self.stdout.write(self.style.WARNING(f"{len(tickets)} overdue ticket(s)"))
