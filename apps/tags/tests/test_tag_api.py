import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.tags.models import Tag


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
def tag(user):
    return Tag.objects.create(
        user=user,
        name="Django",
    )


@pytest.mark.django_db
def test_tag_list_requires_authentication(api_client):
    response = api_client.get("/api/tags/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_can_list_only_own_tags(auth_client, user, other_user):
    own_tag = Tag.objects.create(user=user, name="Django")
    Tag.objects.create(user=other_user, name="Angular")

    response = auth_client.get("/api/tags/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == own_tag.id


@pytest.mark.django_db
def test_user_can_create_tag(auth_client):
    response = auth_client.post(
        "/api/tags/",
        {
            "name": "Backend",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Tag.objects.count() == 1


@pytest.mark.django_db
def test_user_can_retrieve_own_tag(auth_client, tag):
    response = auth_client.get(f"/api/tags/{tag.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == tag.id


@pytest.mark.django_db
def test_user_can_update_own_tag(auth_client, tag):
    response = auth_client.patch(
        f"/api/tags/{tag.id}/",
        {
            "name": "Python",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    tag.refresh_from_db()
    assert tag.name == "Python"


@pytest.mark.django_db
def test_user_can_delete_own_tag(auth_client, tag):
    response = auth_client.delete(f"/api/tags/{tag.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Tag.objects.count() == 0


@pytest.mark.django_db
def test_cannot_create_tag_without_name(auth_client):
    response = auth_client.post(
        "/api/tags/",
        {
            "name": "",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_cannot_create_duplicate_tag(auth_client):
    Tag.objects.create(
        user=auth_client.handler._force_user,
        name="Django",
    )

    response = auth_client.post(
        "/api/tags/",
        {
            "name": "Django",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_can_search_tags(auth_client, user):
    Tag.objects.create(user=user, name="Django")
    Tag.objects.create(user=user, name="Angular")

    response = auth_client.get("/api/tags/?search=django")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_user_can_order_tags_by_name(auth_client, user):
    Tag.objects.create(user=user, name="Python")
    Tag.objects.create(user=user, name="Angular")

    response = auth_client.get("/api/tags/?ordering=name")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["name"] == "Angular"
