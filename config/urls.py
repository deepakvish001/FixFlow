from django.http import JsonResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tickets.api import AssetViewSet, SiteViewSet, TicketViewSet

router = DefaultRouter()
router.register("sites", SiteViewSet)
router.register("assets", AssetViewSet)
router.register("tickets", TicketViewSet)

urlpatterns = [
    path("healthz", lambda request: JsonResponse({"status": "ok"})),
    path("api/", include(router.urls)),
]
