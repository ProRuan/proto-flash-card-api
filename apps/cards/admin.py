from django.contrib import admin

from apps.cards.models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "front",
        "deck",
        "user",
        "is_archived",
        "created_at",
    )
    list_filter = (
        "is_archived",
        "deck",
        "created_at",
    )
    search_fields = (
        "front",
        "back",
        "hint",
        "explanation",
        "deck__name",
        "user__email",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
