from rest_framework import serializers

from apps.decks.models import Deck


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = [
            "id",
            "name",
            "description",
            "topic",
            "slug",
            "is_archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            queryset = Deck.objects.filter(
                user=request.user,
                name=value,
            )

            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)

            if queryset.exists():
                raise serializers.ValidationError(
                    "You already have a deck with this name."
                )

        return value
