# apps/decks/admin.py

from django.contrib import admin

from apps.decks.models import Deck


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "topic",
        "user",
        "is_archived",
        "created_at",
    )

    list_filter = (
        "is_archived",
        "topic",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "topic",
        "user__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "slug",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (
            "General",
            {
                "fields": (
                    "user",
                    "name",
                    "description",
                    "topic",
                    "slug",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_archived",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
