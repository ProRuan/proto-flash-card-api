from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.decks.api.views import DeckViewSet

router = DefaultRouter()
router.register(r"decks", DeckViewSet, basename="deck")

urlpatterns = [
    path("", include(router.urls)),
]
