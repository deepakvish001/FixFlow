from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from tickets.models import Asset, Site, Ticket, TicketEvent
from tickets.sla import deadline_for
from tickets.workflow import InvalidTransition, transition_ticket


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ("id", "name", "address", "active", "created_at")
        read_only_fields = ("id", "created_at")


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ("id", "site", "tag", "name", "category", "serial_number", "active", "created_at")
        read_only_fields = ("id", "created_at")


class TicketEventSerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source="actor.username", allow_null=True, read_only=True)

    class Meta:
        model = TicketEvent
        fields = ("id", "actor", "from_status", "to_status", "note", "created_at")


class TicketSerializer(serializers.ModelSerializer):
    events = TicketEventSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id", "title", "description", "priority", "status", "reported_by", "assigned_to", "asset",
            "due_at", "resolved_at", "closed_at", "created_at", "updated_at", "events",
        )
        read_only_fields = (
            "id", "status", "reported_by", "assigned_to", "resolved_at", "closed_at", "created_at", "updated_at", "events",
        )

    def validate_title(self, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("title must contain at least 3 characters")
        return value

    def create(self, validated_data: dict) -> Ticket:
        validated_data.setdefault("due_at", deadline_for(validated_data.get("priority", Ticket.Priority.NORMAL)))
        return super().create(validated_data)


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.order_by("name")
    serializer_class = SiteSerializer
    permission_classes = (IsAuthenticated,)


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related("site").order_by("tag")
    serializer_class = AssetSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("site", "category", "active")


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("reported_by", "assigned_to", "asset").prefetch_related("events").order_by("-created_at")
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get("overdue", "").lower() == "true":
            queryset = queryset.filter(due_at__lt=timezone.now()).exclude(
                status__in=(Ticket.Status.RESOLVED, Ticket.Status.CLOSED),
            )
        return queryset

    def perform_create(self, serializer: TicketSerializer) -> None:
        serializer.save(reported_by=self.request.user)

    @action(detail=True, methods=("post",))
    def transition(self, request: Request, pk: str | None = None) -> Response:
        ticket = self.get_object()
        assignee = None
        if request.data.get("assigned_to") is not None:
            assignee = get_object_or_404(get_user_model(), pk=request.data["assigned_to"])
        try:
            updated = transition_ticket(
                ticket_id=ticket.id,
                target=str(request.data.get("status", "")),
                actor=request.user,
                note=str(request.data.get("note", "")),
                assigned_to=assignee,
            )
        except InvalidTransition as error:
            raise serializers.ValidationError({"status": str(error)}) from error
        return Response(self.get_serializer(updated).data)
