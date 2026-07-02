from django.contrib import admin

from apps.card_relations.models import CardRelation


@admin.register(CardRelation)
class CardRelationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "from_card",
        "relation_type",
        "to_card",
        "user",
        "created_at",
    )

    list_filter = (
        "relation_type",
        "created_at",
    )

    search_fields = (
        "from_card__front",
        "to_card__front",
        "user__email",
    )

    readonly_fields = (
        "created_at",
    )
