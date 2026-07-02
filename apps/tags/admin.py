# apps/tags/admin.py

from django.contrib import admin

from apps.tags.models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "user",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "user__email",
    )

    readonly_fields = (
        "slug",
        "created_at",
    )

    ordering = ("name",)
