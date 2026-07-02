from rest_framework import serializers

from apps.tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "slug",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "created_at",
        ]

    def validate_name(self, value):
        request = self.context.get("request")
        slug = value.strip().lower().replace(" ", "-")

        if request and request.user.is_authenticated:
            if Tag.objects.filter(user=request.user, slug=slug).exists():
                raise serializers.ValidationError(
                    "You already have a tag with this name."
                )

        return value
