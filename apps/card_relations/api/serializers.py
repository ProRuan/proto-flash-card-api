from rest_framework import serializers

from apps.card_relations.models import CardRelation


class CardRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardRelation
        fields = [
            "id",
            "from_card",
            "to_card",
            "relation_type",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")

        from_card = attrs.get("from_card", getattr(
            self.instance, "from_card", None))
        to_card = attrs.get("to_card", getattr(self.instance, "to_card", None))
        relation_type = attrs.get(
            "relation_type",
            getattr(self.instance, "relation_type", None),
        )

        if from_card == to_card:
            raise serializers.ValidationError(
                "A card cannot be related to itself."
            )

        if request and request.user.is_authenticated:
            if from_card.user != request.user or to_card.user != request.user:
                raise serializers.ValidationError(
                    "You can only relate your own cards."
                )

            queryset = CardRelation.objects.filter(
                from_card=from_card,
                to_card=to_card,
                relation_type=relation_type,
            )

            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)

            if queryset.exists():
                raise serializers.ValidationError(
                    "This card relation already exists."
                )

        return attrs
