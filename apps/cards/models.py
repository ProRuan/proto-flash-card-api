from django.conf import settings
from django.db import models


class Card(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    deck = models.ForeignKey(
        "decks.Deck",
        on_delete=models.CASCADE,
        related_name="cards",
    )
    front = models.TextField()
    back = models.TextField()
    hint = models.TextField(blank=True)
    explanation = models.TextField(blank=True)

    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "deck"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return self.front[:80]
