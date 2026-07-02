import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

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
        name="Software Engineering",
        description="General software engineering knowledge.",
        topic="Software Engineering",
    )


@pytest.mark.django_db
def test_deck_list_requires_authentication(api_client):
    response = api_client.get("/api/decks/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_can_list_only_own_decks(auth_client, user, other_user):
    own_deck = Deck.objects.create(user=user, name="Own Deck")
    Deck.objects.create(user=other_user, name="Other Deck")

    response = auth_client.get("/api/decks/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == own_deck.id


@pytest.mark.django_db
def test_user_can_create_deck(auth_client, user):
    payload = {
        "name": "Django",
        "description": "Django REST Framework basics.",
        "topic": "Backend",
    }

    response = auth_client.post("/api/decks/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Deck.objects.count() == 1

    deck = Deck.objects.first()
    assert deck.user == user
    assert deck.name == "Django"
    assert deck.topic == "Backend"


@pytest.mark.django_db
def test_user_can_retrieve_own_deck(auth_client, deck):
    response = auth_client.get(f"/api/decks/{deck.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == deck.id
    assert response.data["name"] == deck.name


@pytest.mark.django_db
def test_user_cannot_retrieve_other_users_deck(auth_client, other_user):
    other_deck = Deck.objects.create(user=other_user, name="Private Deck")

    response = auth_client.get(f"/api/decks/{other_deck.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_user_can_update_own_deck(auth_client, deck):
    payload = {
        "name": "Updated Deck",
        "topic": "Updated Topic",
    }

    response = auth_client.patch(
        f"/api/decks/{deck.id}/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    deck.refresh_from_db()
    assert deck.name == "Updated Deck"
    assert deck.topic == "Updated Topic"


@pytest.mark.django_db
def test_user_can_delete_own_deck(auth_client, deck):
    response = auth_client.delete(f"/api/decks/{deck.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Deck.objects.count() == 0


@pytest.mark.django_db
def test_user_can_search_decks(auth_client, user):
    Deck.objects.create(user=user, name="Django Basics", topic="Backend")
    Deck.objects.create(user=user, name="Angular Basics", topic="Frontend")

    response = auth_client.get("/api/decks/?search=django")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "Django Basics"


@pytest.mark.django_db
def test_user_can_filter_decks_by_topic(auth_client, user):
    Deck.objects.create(user=user, name="Django Basics", topic="Backend")
    Deck.objects.create(user=user, name="Angular Basics", topic="Frontend")

    response = auth_client.get("/api/decks/?topic=Backend")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["topic"] == "Backend"


@pytest.mark.django_db
def test_user_can_filter_archived_decks(auth_client, user):
    Deck.objects.create(user=user, name="Active Deck", is_archived=False)
    Deck.objects.create(user=user, name="Archived Deck", is_archived=True)

    response = auth_client.get("/api/decks/?is_archived=true")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "Archived Deck"


@pytest.mark.django_db
def test_user_can_order_decks_by_name(auth_client, user):
    Deck.objects.create(user=user, name="Beta")
    Deck.objects.create(user=user, name="Alpha")

    response = auth_client.get("/api/decks/?ordering=name")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["name"] == "Alpha"
    assert response.data["results"][1]["name"] == "Beta"


@pytest.mark.django_db
def test_cannot_create_deck_without_name(auth_client):
    response = auth_client.post(
        "/api/decks/",
        {
            "name": "",
            "description": "Missing name.",
            "topic": "Backend",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data


@pytest.mark.django_db
def test_cannot_create_deck_with_too_long_name(auth_client):
    response = auth_client.post(
        "/api/decks/",
        {
            "name": "a" * 121,
            "description": "Too long name.",
            "topic": "Backend",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data


@pytest.mark.django_db
def test_user_cannot_create_duplicate_deck_name(auth_client, user):
    Deck.objects.create(
        user=user,
        name="Django",
    )

    response = auth_client.post(
        "/api/decks/",
        {
            "name": "Django",
            "description": "Duplicate deck.",
            "topic": "Backend",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_can_create_same_deck_name_as_other_user(auth_client, other_user):
    Deck.objects.create(
        user=other_user,
        name="Django",
    )

    response = auth_client.post(
        "/api/decks/",
        {
            "name": "Django",
            "description": "Own Django deck.",
            "topic": "Backend",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_user_cannot_update_other_users_deck(auth_client, other_user):
    other_deck = Deck.objects.create(
        user=other_user,
        name="Private Deck",
    )

    response = auth_client.patch(
        f"/api/decks/{other_deck.id}/",
        {
            "name": "Hacked Deck",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    other_deck.refresh_from_db()
    assert other_deck.name == "Private Deck"


@pytest.mark.django_db
def test_user_cannot_delete_other_users_deck(auth_client, other_user):
    other_deck = Deck.objects.create(
        user=other_user,
        name="Private Deck",
    )

    response = auth_client.delete(f"/api/decks/{other_deck.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Deck.objects.filter(id=other_deck.id).exists()
