import pytest
from uuid import uuid4
from app.factories.category_factory import CategoryFactory
from app.schemas.category_schema import Category, CategoryCustom
from app.enums.category_enums import PredefinedCategory


class TestCategoryFactoryPredefined:

    def test_returns_category_instance(self):
        result = CategoryFactory.create_predefined(uuid4(), PredefinedCategory.TECHNOLOGY)
        assert isinstance(result, Category)

    def test_name_equals_enum_value(self):
        result = CategoryFactory.create_predefined(uuid4(), PredefinedCategory.COSMETICS)
        assert result.name == "Cosmetics"

    def test_clothing_name(self):
        result = CategoryFactory.create_predefined(uuid4(), PredefinedCategory.CLOTHING)
        assert result.name == "Clothing"

    def test_kitchen_name(self):
        result = CategoryFactory.create_predefined(uuid4(), PredefinedCategory.KITCHEN)
        assert result.name == "Kitchen Utensils"

    def test_category_type_equals_enum_name(self):
        result = CategoryFactory.create_predefined(uuid4(), PredefinedCategory.CLOTHING)
        assert result.category_type == "CLOTHING"

    def test_user_id_is_set_correctly(self):
        user_id = uuid4()
        result = CategoryFactory.create_predefined(user_id, PredefinedCategory.KITCHEN)
        assert result.user_id == user_id

    def test_id_is_none_before_save(self):
        result = CategoryFactory.create_predefined(uuid4(), PredefinedCategory.TECHNOLOGY)
        assert result.id is None

    def test_different_user_ids_produce_different_categories(self):
        uid1, uid2 = uuid4(), uuid4()
        r1 = CategoryFactory.create_predefined(uid1, PredefinedCategory.TECHNOLOGY)
        r2 = CategoryFactory.create_predefined(uid2, PredefinedCategory.TECHNOLOGY)
        assert r1.user_id != r2.user_id

    @pytest.mark.parametrize("category_type,expected_name", [
        (PredefinedCategory.COSMETICS, "Cosmetics"),
        (PredefinedCategory.CLOTHING, "Clothing"),
        (PredefinedCategory.TECHNOLOGY, "Technology"),
        (PredefinedCategory.KITCHEN, "Kitchen Utensils"),
    ])
    def test_all_predefined_names_are_correct(self, category_type, expected_name):
        result = CategoryFactory.create_predefined(uuid4(), category_type)
        assert result.name == expected_name

    @pytest.mark.parametrize("category_type", list(PredefinedCategory))
    def test_all_predefined_have_no_id(self, category_type):
        result = CategoryFactory.create_predefined(uuid4(), category_type)
        assert result.id is None


class TestCategoryFactoryCustom:

    def test_returns_category_instance(self):
        custom = CategoryCustom(name="Books", category_type="BOOKS")
        result = CategoryFactory.create_custom(uuid4(), custom)
        assert isinstance(result, Category)

    def test_name_is_preserved(self):
        custom = CategoryCustom(name="My Books", category_type="BOOKS")
        result = CategoryFactory.create_custom(uuid4(), custom)
        assert result.name == "My Books"

    def test_category_type_is_preserved(self):
        custom = CategoryCustom(name="Sports", category_type="SPORTS")
        result = CategoryFactory.create_custom(uuid4(), custom)
        assert result.category_type == "SPORTS"

    def test_user_id_is_set_correctly(self):
        user_id = uuid4()
        custom = CategoryCustom(name="Hobby", category_type="HOBBY")
        result = CategoryFactory.create_custom(user_id, custom)
        assert result.user_id == user_id

    def test_id_is_none_before_save(self):
        custom = CategoryCustom(name="Games", category_type="GAMES")
        result = CategoryFactory.create_custom(uuid4(), custom)
        assert result.id is None

    def test_name_with_spaces_preserved(self):
        custom = CategoryCustom(name="Home Decor", category_type="HOME_DECOR")
        result = CategoryFactory.create_custom(uuid4(), custom)
        assert result.name == "Home Decor"

    def test_different_users_same_custom_name(self):
        custom = CategoryCustom(name="Books", category_type="BOOKS")
        uid1, uid2 = uuid4(), uuid4()
        r1 = CategoryFactory.create_custom(uid1, custom)
        r2 = CategoryFactory.create_custom(uid2, custom)
        assert r1.user_id != r2.user_id
        assert r1.name == r2.name
