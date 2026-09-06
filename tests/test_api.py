import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tickets.models import Ticket


@pytest.mark.django_db
def test_authenticated_ticket_creation_and_transition() -> None:
    users = get_user_model()
    reporter = users.objects.create_user(username="reporter")
    technician = users.objects.create_user(username="technician")
    client = APIClient()
    client.force_authenticate(reporter)

    created = client.post("/api/tickets/", {"title": "Leaking pipe", "description": "Room 2", "priority": "high"}, format="json")
    assert created.status_code == 201
    assert created.data["reported_by"] == reporter.id
    transitioned = client.post(
        f"/api/tickets/{created.data['id']}/transition/",
        {"status": "assigned", "assigned_to": technician.id, "note": "Dispatch"},
        format="json",
    )
    assert transitioned.status_code == 200
    assert transitioned.data["status"] == Ticket.Status.ASSIGNED
    assert transitioned.data["events"][0]["note"] == "Dispatch"


@pytest.mark.django_db
def test_api_requires_authentication_and_protects_direct_status_updates() -> None:
    user = get_user_model().objects.create_user(username="reporter")
    ticket = Ticket.objects.create(title="Broken lock", description="Store room", reported_by=user)
    anonymous = APIClient()
    assert anonymous.get("/api/tickets/").status_code in {401, 403}

    client = APIClient()
    client.force_authenticate(user)
    response = client.patch(f"/api/tickets/{ticket.id}/", {"status": "closed"}, format="json")
    assert response.status_code == 200
    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.OPEN
