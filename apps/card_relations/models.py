from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class CardRelation(models.Model):

    class RelationType(models.TextChoices):
        PARENT = "parent", "Parent"
        SIBLING = "sibling", "Sibling"
        CHILD = "child", "Child"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="card_relations",
    )

    from_card = models.ForeignKey(
        "cards.Card",
        on_delete=models.CASCADE,
        related_name="outgoing_relations",
    )

    to_card = models.ForeignKey(
        "cards.Card",
        on_delete=models.CASCADE,
        related_name="incoming_relations",
    )

    relation_type = models.CharField(
        max_length=20,
        choices=RelationType.choices,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "from_card",
                    "to_card",
                    "relation_type",
                ],
                name="unique_card_relation",
            )
        ]

    def __str__(self):
        return (
            f"{self.from_card_id} "
            f"{self.relation_type} "
            f"{self.to_card_id}"
        )

    def clean(self):
        if self.from_card == self.to_card:
            raise ValidationError(
                "A card cannot be related to itself."
            )
