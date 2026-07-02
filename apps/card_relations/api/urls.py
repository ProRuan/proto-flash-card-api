from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.card_relations.api.views import CardRelationViewSet

router = DefaultRouter()
router.register("card-relations", CardRelationViewSet,
                basename="card-relation")

urlpatterns = [
    path("", include(router.urls)),
]
