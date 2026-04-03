import pytest
from unittest.mock import patch
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_USER_ID = uuid4()


def make_category(name="Technology", category_type="TECHNOLOGY", user_id=None):
    return {
        "id": str(uuid4()),
        "name": name,
        "user_id": str(user_id or TEST_USER_ID),
        "category_type": category_type,
        "created_at": "2024-01-01T00:00:00",
    }


DEFAULT_CATEGORIES = [
    make_category("Cosmetics", "COSMETICS"),
    make_category("Clothing", "CLOTHING"),
    make_category("Technology", "TECHNOLOGY"),
    make_category("Kitchen Utensils", "KITCHEN"),
]


class TestListCategoriesEndpoint:

    def test_returns_200_when_categories_exist(self):
        with patch("app.api.category_router.service.list_user_categories", return_value=DEFAULT_CATEGORIES):
            response = client.get(f"/users/{TEST_USER_ID}/list-categories")
        assert response.status_code == 200

    def test_response_is_list(self):
        with patch("app.api.category_router.service.list_user_categories", return_value=DEFAULT_CATEGORIES):
            response = client.get(f"/users/{TEST_USER_ID}/list-categories")
        assert isinstance(response.json(), list)

    def test_returns_correct_number_of_categories(self):
        with patch("app.api.category_router.service.list_user_categories", return_value=DEFAULT_CATEGORIES):
            response = client.get(f"/users/{TEST_USER_ID}/list-categories")
        assert len(response.json()) == 4

    def test_initializes_defaults_when_list_is_empty(self):
        with patch("app.api.category_router.service.list_user_categories", return_value=[]), \
             patch("app.api.category_router.service.initialize_default_categories", return_value=DEFAULT_CATEGORIES) as mock_init:
            client.get(f"/users/{TEST_USER_ID}/list-categories")
            mock_init.assert_called_once()

    def test_does_not_initialize_when_categories_exist(self):
        with patch("app.api.category_router.service.list_user_categories", return_value=DEFAULT_CATEGORIES), \
             patch("app.api.category_router.service.initialize_default_categories") as mock_init:
            client.get(f"/users/{TEST_USER_ID}/list-categories")
            mock_init.assert_not_called()

    def test_invalid_user_id_returns_422(self):
        response = client.get("/users/not-a-uuid/list-categories")
        assert response.status_code == 422

    def test_category_has_name_field(self):
        with patch("app.api.category_router.service.list_user_categories", return_value=DEFAULT_CATEGORIES):
            response = client.get(f"/users/{TEST_USER_ID}/list-categories")
        assert "name" in response.json()[0]

    def test_category_has_id_field(self):
        with patch("app.api.category_router.service.list_user_categories", return_value=DEFAULT_CATEGORIES):
            response = client.get(f"/users/{TEST_USER_ID}/list-categories")
        assert "id" in response.json()[0]


class TestInitializeCategoriesEndpoint:

    def test_returns_200_on_success(self):
        with patch("app.api.category_router.service.initialize_default_categories", return_value=DEFAULT_CATEGORIES):
            response = client.post(f"/users/{TEST_USER_ID}/initialize-categories")
        assert response.status_code == 200

    def test_response_contains_four_categories(self):
        with patch("app.api.category_router.service.initialize_default_categories", return_value=DEFAULT_CATEGORIES):
            response = client.post(f"/users/{TEST_USER_ID}/initialize-categories")
        assert len(response.json()) == 4

    def test_response_includes_technology(self):
        with patch("app.api.category_router.service.initialize_default_categories", return_value=DEFAULT_CATEGORIES):
            response = client.post(f"/users/{TEST_USER_ID}/initialize-categories")
        names = [c["name"] for c in response.json()]
        assert "Technology" in names

    def test_invalid_user_id_returns_422(self):
        response = client.post("/users/bad-uuid/initialize-categories")
        assert response.status_code == 422

    def test_service_called_with_correct_user_id(self):
        uid = uuid4()
        with patch("app.api.category_router.service.initialize_default_categories", return_value=[]) as mock_svc:
            client.post(f"/users/{uid}/initialize-categories")
            mock_svc.assert_called_once_with(uid)


class TestAddNewCategoryEndpoint:

    def test_returns_200_on_valid_request(self):
        new_cat = make_category("Books", "BOOKS")
        with patch("app.api.category_router.service.create_new_category", return_value=new_cat):
            response = client.post(
                f"/users/{TEST_USER_ID}/add-new-category",
                json={"name": "Books", "category_type": "BOOKS"},
            )
        assert response.status_code == 200

    def test_response_contains_category_name(self):
        new_cat = make_category("Sports", "SPORTS")
        with patch("app.api.category_router.service.create_new_category", return_value=new_cat):
            response = client.post(
                f"/users/{TEST_USER_ID}/add-new-category",
                json={"name": "Sports", "category_type": "SPORTS"},
            )
        assert response.json()["name"] == "Sports"

    def test_missing_name_returns_422(self):
        response = client.post(
            f"/users/{TEST_USER_ID}/add-new-category",
            json={"category_type": "BOOKS"},
        )
        assert response.status_code == 422

    def test_missing_category_type_returns_422(self):
        response = client.post(
            f"/users/{TEST_USER_ID}/add-new-category",
            json={"name": "Books"},
        )
        assert response.status_code == 422

    def test_empty_body_returns_422(self):
        response = client.post(f"/users/{TEST_USER_ID}/add-new-category", json={})
        assert response.status_code == 422

    def test_invalid_user_id_returns_422(self):
        response = client.post(
            "/users/not-a-uuid/add-new-category",
            json={"name": "Books", "category_type": "BOOKS"},
        )
        assert response.status_code == 422
