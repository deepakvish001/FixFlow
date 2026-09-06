import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from tickets.models import Asset, Site, Ticket


@pytest.mark.django_db
def test_site_asset_and_ticket_relationships() -> None:
    user = get_user_model().objects.create_user(username="reporter")
    site = Site.objects.create(name="North Campus", address="Building A")
    asset = Asset.objects.create(site=site, tag="HVAC-001", name="Rooftop HVAC", category="climate")
    ticket = Ticket.objects.create(title="Unexpected vibration", description="Unit vibrates", reported_by=user, asset=asset)

    assert ticket.asset == asset
    assert list(asset.tickets.all()) == [ticket]
    assert str(asset) == "HVAC-001: Rooftop HVAC"


@pytest.mark.django_db(transaction=True)
def test_asset_tags_are_unique() -> None:
    site = Site.objects.create(name="Warehouse")
    Asset.objects.create(site=site, tag="LIFT-01", name="Lift", category="material handling")
    with pytest.raises(IntegrityError):
        Asset.objects.create(site=site, tag="LIFT-01", name="Other lift", category="material handling")
