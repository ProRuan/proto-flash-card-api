from rest_framework import serializers

from apps.cards.models import Card
from apps.decks.models import Deck


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            "id",
            "deck",
            "front",
            "back",
            "hint",
            "explanation",
            "is_archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_deck(self, value):
        request = self.context.get("request")

        if request and value.user != request.user:
            raise serializers.ValidationError(
                "You can only create cards in your own decks."
            )

        return value
