import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from app.services.category_service import CategoryService
from app.schemas.category_schema import Category, CategoryCustom
from app.enums.category_enums import PredefinedCategory


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return CategoryService(mock_repo)


def make_saved_category(user_id, name, category_type):
    return Category(id=uuid4(), name=name, user_id=user_id, category_type=category_type)


class TestInitializeDefaultCategories:

    def test_creates_one_category_per_predefined_enum(self, service, mock_repo):
        user_id = uuid4()
        mock_repo.save.side_effect = lambda cat: make_saved_category(user_id, cat.name, cat.category_type)
        result = service.initialize_default_categories(user_id)
        assert len(result) == len(list(PredefinedCategory))

    def test_repository_save_called_four_times(self, service, mock_repo):
        mock_repo.save.return_value = MagicMock(spec=Category)
        service.initialize_default_categories(uuid4())
        assert mock_repo.save.call_count == 4

    def test_returns_list_of_categories(self, service, mock_repo):
        user_id = uuid4()
        mock_repo.save.side_effect = lambda cat: make_saved_category(user_id, cat.name, cat.category_type)
        result = service.initialize_default_categories(user_id)
        assert isinstance(result, list)
        assert all(isinstance(c, Category) for c in result)

    def test_saved_categories_have_ids(self, service, mock_repo):
        user_id = uuid4()
        mock_repo.save.side_effect = lambda cat: make_saved_category(user_id, cat.name, cat.category_type)
        result = service.initialize_default_categories(user_id)
        assert all(c.id is not None for c in result)

    def test_category_names_match_predefined_values(self, service, mock_repo):
        user_id = uuid4()
        mock_repo.save.side_effect = lambda cat: make_saved_category(user_id, cat.name, cat.category_type)
        result = service.initialize_default_categories(user_id)
        names = {c.name for c in result}
        expected = {e.value for e in PredefinedCategory}
        assert names == expected

    def test_all_categories_belong_to_correct_user(self, service, mock_repo):
        user_id = uuid4()
        mock_repo.save.side_effect = lambda cat: make_saved_category(user_id, cat.name, cat.category_type)
        result = service.initialize_default_categories(user_id)
        assert all(c.user_id == user_id for c in result)


class TestListUserCategories:

    def test_delegates_to_repository_find_by_user(self, service, mock_repo):
        user_id = uuid4()
        mock_repo.find_by_user.return_value = []
        service.list_user_categories(user_id)
        mock_repo.find_by_user.assert_called_once_with(user_id)

    def test_returns_list_from_repository(self, service, mock_repo):
        user_id = uuid4()
        expected = [make_saved_category(user_id, "Technology", "TECHNOLOGY")]
        mock_repo.find_by_user.return_value = expected
        result = service.list_user_categories(user_id)
        assert result == expected

    def test_returns_empty_list_when_no_categories(self, service, mock_repo):
        mock_repo.find_by_user.return_value = []
        result = service.list_user_categories(uuid4())
        assert result == []

    def test_does_not_call_save(self, service, mock_repo):
        mock_repo.find_by_user.return_value = []
        service.list_user_categories(uuid4())
        mock_repo.save.assert_not_called()


class TestCreateNewCategory:

    def test_calls_repository_save(self, service, mock_repo):
        user_id = uuid4()
        custom = CategoryCustom(name="Books", category_type="BOOKS")
        mock_repo.save.return_value = make_saved_category(user_id, "Books", "BOOKS")
        service.create_new_category(user_id, custom)
        mock_repo.save.assert_called_once()

    def test_saved_category_has_correct_name(self, service, mock_repo):
        user_id = uuid4()
        custom = CategoryCustom(name="Sports", category_type="SPORTS")
        expected = make_saved_category(user_id, "Sports", "SPORTS")
        mock_repo.save.return_value = expected
        result = service.create_new_category(user_id, custom)
        assert result.name == "Sports"

    def test_returns_saved_category(self, service, mock_repo):
        user_id = uuid4()
        custom = CategoryCustom(name="Pets", category_type="PETS")
        expected = make_saved_category(user_id, "Pets", "PETS")
        mock_repo.save.return_value = expected
        result = service.create_new_category(user_id, custom)
        assert result is expected

    def test_saved_category_has_user_id(self, service, mock_repo):
        user_id = uuid4()
        custom = CategoryCustom(name="Travel", category_type="TRAVEL")
        mock_repo.save.side_effect = lambda cat: make_saved_category(cat.user_id, cat.name, cat.category_type)
        result = service.create_new_category(user_id, custom)
        assert result.user_id == user_id
