from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from apps.decks.api.permissions import IsDeckOwner
from apps.decks.api.serializers import DeckSerializer
from apps.decks.models import Deck


class DeckViewSet(viewsets.ModelViewSet):
    serializer_class = DeckSerializer
    permission_classes = [IsAuthenticated, IsDeckOwner]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "topic",
        "is_archived",
    ]

    search_fields = [
        "name",
        "description",
        "topic",
    ]

    ordering_fields = [
        "name",
        "topic",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        return Deck.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
