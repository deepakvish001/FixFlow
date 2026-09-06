import pytest
from django.test import override_settings


def test_security_defaults_are_enabled() -> None:
    from django.conf import settings

    assert settings.DEBUG is False
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.X_FRAME_OPTIONS == "DENY"
    assert settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] == (
        "rest_framework.authentication.TokenAuthentication",
    )


@override_settings(ALLOWED_HOSTS=["testserver"])
@pytest.mark.django_db
def test_health_check_remains_public(client) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
