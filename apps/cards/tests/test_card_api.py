import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

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
def card(user, deck):
    return Card.objects.create(
        user=user,
        deck=deck,
        front="What is DRF?",
        back="Django REST Framework.",
        hint="API toolkit",
    )


@pytest.mark.django_db
def test_card_list_requires_authentication(api_client):
    response = api_client.get("/api/cards/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_can_list_only_own_cards(auth_client, user, deck, other_user, other_deck):
    own_card = Card.objects.create(
        user=user,
        deck=deck,
        front="Own card",
        back="Own answer",
    )
    Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Other card",
        back="Other answer",
    )

    response = auth_client.get("/api/cards/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == own_card.id


@pytest.mark.django_db
def test_user_can_create_card(auth_client, user, deck):
    payload = {
        "deck": deck.id,
        "front": "What is Django?",
        "back": "A Python web framework.",
        "hint": "Python",
        "explanation": "Django is used to build web applications.",
    }

    response = auth_client.post("/api/cards/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Card.objects.count() == 1

    card = Card.objects.first()
    assert card.user == user
    assert card.deck == deck
    assert card.front == "What is Django?"


@pytest.mark.django_db
def test_user_cannot_create_card_in_other_users_deck(auth_client, other_deck):
    payload = {
        "deck": other_deck.id,
        "front": "Invalid card",
        "back": "Should not work.",
    }

    response = auth_client.post("/api/cards/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Card.objects.count() == 0


@pytest.mark.django_db
def test_user_can_retrieve_own_card(auth_client, card):
    response = auth_client.get(f"/api/cards/{card.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == card.id
    assert response.data["front"] == card.front


@pytest.mark.django_db
def test_user_cannot_retrieve_other_users_card(auth_client, other_user, other_deck):
    other_card = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Private card",
        back="Private answer",
    )

    response = auth_client.get(f"/api/cards/{other_card.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_user_can_update_own_card(auth_client, card):
    response = auth_client.patch(
        f"/api/cards/{card.id}/",
        {
            "front": "Updated question",
            "back": "Updated answer",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    card.refresh_from_db()
    assert card.front == "Updated question"
    assert card.back == "Updated answer"


@pytest.mark.django_db
def test_user_cannot_update_other_users_card(auth_client, other_user, other_deck):
    other_card = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Private card",
        back="Private answer",
    )

    response = auth_client.patch(
        f"/api/cards/{other_card.id}/",
        {
            "front": "Hacked question",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    other_card.refresh_from_db()
    assert other_card.front == "Private card"


@pytest.mark.django_db
def test_user_can_delete_own_card(auth_client, card):
    response = auth_client.delete(f"/api/cards/{card.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Card.objects.count() == 0


@pytest.mark.django_db
def test_user_cannot_delete_other_users_card(auth_client, other_user, other_deck):
    other_card = Card.objects.create(
        user=other_user,
        deck=other_deck,
        front="Private card",
        back="Private answer",
    )

    response = auth_client.delete(f"/api/cards/{other_card.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Card.objects.filter(id=other_card.id).exists()
