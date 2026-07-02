import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.card_relations.models import CardRelation
from apps.cards.models import Card
from apps.decks.models import Deck


User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com",
        password="testpass123",
    )


@pytest.fixture
def other_user():
    return User.objects.create_user(
        email="other@example.com",
        password="testpass123",
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def deck(user):
    return Deck.objects.create(
        user=user,
        name="Django",
        topic="Backend",
    )


@pytest.fixture
def other_deck(other_user):
    return Deck.objects.create(
        user=other_user,
        name="Private Deck",
    )


@pytest.fixture
def card_a(user, deck):
    return Card.objects.create(
        user=user,
        deck=deck,
        front="Parent card",
        back="Parent answer",
    )


@pytest.fixture
def card_b(user, deck):
    return Card.objects.create(
        user=user,
        deck=deck,
        front="Child card",
        back="Child answer",
    )


@pytest.fixture
def other_card(other_user, other_deck):
    return Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Other card",
        back="Other answer",
    )


@pytest.fixture
def relation(user, card_a, card_b):
    return CardRelation.objects.create(
        user=user,
        from_card=card_a,
        to_card=card_b,
        relation_type=CardRelation.RelationType.CHILD,
    )


@pytest.mark.django_db
def test_card_relation_list_requires_authentication(api_client):
    response = api_client.get("/api/card-relations/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_can_list_only_own_card_relations(
    auth_client,
    user,
    card_a,
    card_b,
    other_user,
    other_card,
    other_deck,
):
    own_relation = CardRelation.objects.create(
        user=user,
        from_card=card_a,
        to_card=card_b,
        relation_type=CardRelation.RelationType.CHILD,
    )

    other_second_card = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Other second card",
        back="Other second answer",
    )

    CardRelation.objects.create(
        user=other_user,
        from_card=other_card,
        to_card=other_second_card,
        relation_type=CardRelation.RelationType.CHILD,
    )

    response = auth_client.get("/api/card-relations/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == own_relation.id


@pytest.mark.django_db
def test_user_can_create_card_relation(auth_client, card_a, card_b):
    payload = {
        "from_card": card_a.id,
        "to_card": card_b.id,
        "relation_type": "child",
    }

    response = auth_client.post(
        "/api/card-relations/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert CardRelation.objects.count() == 1

    relation = CardRelation.objects.first()
    assert relation.from_card == card_a
    assert relation.to_card == card_b
    assert relation.relation_type == CardRelation.RelationType.CHILD


@pytest.mark.django_db
def test_user_cannot_create_relation_with_other_users_card(
    auth_client,
    card_a,
    other_card,
):
    payload = {
        "from_card": card_a.id,
        "to_card": other_card.id,
        "relation_type": "child",
    }

    response = auth_client.post(
        "/api/card-relations/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert CardRelation.objects.count() == 0


@pytest.mark.django_db
def test_user_cannot_relate_card_to_itself(auth_client, card_a):
    payload = {
        "from_card": card_a.id,
        "to_card": card_a.id,
        "relation_type": "child",
    }

    response = auth_client.post(
        "/api/card-relations/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert CardRelation.objects.count() == 0


@pytest.mark.django_db
def test_user_cannot_create_duplicate_card_relation(
    auth_client,
    user,
    card_a,
    card_b,
):
    CardRelation.objects.create(
        user=user,
        from_card=card_a,
        to_card=card_b,
        relation_type=CardRelation.RelationType.CHILD,
    )

    payload = {
        "from_card": card_a.id,
        "to_card": card_b.id,
        "relation_type": "child",
    }

    response = auth_client.post(
        "/api/card-relations/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert CardRelation.objects.count() == 1


@pytest.mark.django_db
def test_user_can_retrieve_own_card_relation(auth_client, relation):
    response = auth_client.get(f"/api/card-relations/{relation.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == relation.id


@pytest.mark.django_db
def test_user_can_update_own_card_relation(auth_client, relation):
    response = auth_client.patch(
        f"/api/card-relations/{relation.id}/",
        {
            "relation_type": "sibling",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    relation.refresh_from_db()
    assert relation.relation_type == CardRelation.RelationType.SIBLING


@pytest.mark.django_db
def test_user_can_delete_own_card_relation(auth_client, relation):
    response = auth_client.delete(f"/api/card-relations/{relation.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert CardRelation.objects.count() == 0


@pytest.mark.django_db
def test_user_can_filter_card_relations_by_relation_type(
    auth_client,
    user,
    card_a,
    card_b,
    deck,
):
    card_c = Card.objects.create(
        user=user,
        deck=deck,
        front="Sibling card",
        back="Sibling answer",
    )

    CardRelation.objects.create(
        user=user,
        from_card=card_a,
        to_card=card_b,
        relation_type=CardRelation.RelationType.CHILD,
    )
    CardRelation.objects.create(
        user=user,
        from_card=card_a,
        to_card=card_c,
        relation_type=CardRelation.RelationType.SIBLING,
    )

    response = auth_client.get("/api/card-relations/?relation_type=child")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["relation_type"] == "child"


@pytest.mark.django_db
def test_user_can_filter_card_relations_by_from_card(
    auth_client,
    user,
    card_a,
    card_b,
    deck,
):
    card_c = Card.objects.create(
        user=user,
        deck=deck,
        front="Another source card",
        back="Another source answer",
    )

    CardRelation.objects.create(
        user=user,
        from_card=card_a,
        to_card=card_b,
        relation_type=CardRelation.RelationType.CHILD,
    )
    CardRelation.objects.create(
        user=user,
        from_card=card_c,
        to_card=card_b,
        relation_type=CardRelation.RelationType.PARENT,
    )

    response = auth_client.get(f"/api/card-relations/?from_card={card_a.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["from_card"] == card_a.id


@pytest.mark.django_db
def test_user_cannot_retrieve_other_users_card_relation(
    auth_client,
    other_user,
    other_deck,
):
    other_card_a = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Other parent card",
        back="Other parent answer",
    )
    other_card_b = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Other child card",
        back="Other child answer",
    )
    other_relation = CardRelation.objects.create(
        user=other_user,
        from_card=other_card_a,
        to_card=other_card_b,
        relation_type=CardRelation.RelationType.CHILD,
    )

    response = auth_client.get(f"/api/card-relations/{other_relation.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_user_cannot_update_other_users_card_relation(
    auth_client,
    other_user,
    other_deck,
):
    other_card_a = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Other parent card",
        back="Other parent answer",
    )
    other_card_b = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Other child card",
        back="Other child answer",
    )
    other_relation = CardRelation.objects.create(
        user=other_user,
        from_card=other_card_a,
        to_card=other_card_b,
        relation_type=CardRelation.RelationType.CHILD,
    )

    response = auth_client.patch(
        f"/api/card-relations/{other_relation.id}/",
        {
            "relation_type": "sibling",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    other_relation.refresh_from_db()
    assert other_relation.relation_type == CardRelation.RelationType.CHILD


@pytest.mark.django_db
def test_user_cannot_delete_other_users_card_relation(
    auth_client,
    other_user,
    other_deck,
):
    other_card_a = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Other parent card",
        back="Other parent answer",
    )
    other_card_b = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Other child card",
        back="Other child answer",
    )
    other_relation = CardRelation.objects.create(
        user=other_user,
        from_card=other_card_a,
        to_card=other_card_b,
        relation_type=CardRelation.RelationType.CHILD,
    )

    response = auth_client.delete(f"/api/card-relations/{other_relation.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert CardRelation.objects.filter(id=other_relation.id).exists()
