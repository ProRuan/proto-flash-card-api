from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from apps.card_relations.api.permissions import IsCardRelationOwner
from apps.card_relations.api.serializers import CardRelationSerializer
from apps.card_relations.models import CardRelation


class CardRelationViewSet(viewsets.ModelViewSet):
    serializer_class = CardRelationSerializer
    permission_classes = [IsAuthenticated, IsCardRelationOwner]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = [
        "from_card",
        "to_card",
        "relation_type",
    ]

    ordering_fields = [
        "relation_type",
        "created_at",
    ]

    ordering = ["created_at"]

    def get_queryset(self):
        return CardRelation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
