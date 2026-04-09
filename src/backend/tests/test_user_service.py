import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime
from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate, UserRead


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return UserService(mock_repo)


def make_user_read(first_name="Ali", last_name="Veli", email="ali@example.com"):
    return UserRead(
        id=uuid4(),
        first_name=first_name,
        last_name=last_name,
        email=email,
        created_at=datetime.now(),
    )


class TestCreateUser:

    def test_calls_repository_save(self, service, mock_repo):
        mock_repo.save.return_value = make_user_read()
        service.create_user("Ali", "Veli", "ali@example.com")
        mock_repo.save.assert_called_once()

    def test_passes_correct_first_name(self, service, mock_repo):
        mock_repo.save.return_value = make_user_read()
        service.create_user("Zeynep", "Kaya", "zeynep@example.com")
        saved_user = mock_repo.save.call_args[0][0]
        assert saved_user.first_name == "Zeynep"

    def test_passes_correct_last_name(self, service, mock_repo):
        mock_repo.save.return_value = make_user_read()
        service.create_user("Mehmet", "Yılmaz", "mehmet@example.com")
        saved_user = mock_repo.save.call_args[0][0]
        assert saved_user.last_name == "Yılmaz"

    def test_passes_correct_email(self, service, mock_repo):
        mock_repo.save.return_value = make_user_read()
        service.create_user("Can", "Öz", "can@example.com")
        saved_user = mock_repo.save.call_args[0][0]
        assert saved_user.email == "can@example.com"

    def test_passes_user_create_schema_to_repo(self, service, mock_repo):
        mock_repo.save.return_value = make_user_read()
        service.create_user("Test", "User", "test@example.com")
        saved_user = mock_repo.save.call_args[0][0]
        assert isinstance(saved_user, UserCreate)

    def test_returns_saved_user(self, service, mock_repo):
        expected = make_user_read()
        mock_repo.save.return_value = expected
        result = service.create_user("Ali", "Veli", "ali@example.com")
        assert result is expected

    def test_returns_user_with_id(self, service, mock_repo):
        expected = make_user_read()
        mock_repo.save.return_value = expected
        result = service.create_user("Ali", "Veli", "ali@example.com")
        assert result.id is not None

    def test_different_emails_produce_different_save_calls(self, service, mock_repo):
        mock_repo.save.return_value = make_user_read()
        service.create_user("A", "B", "first@example.com")
        service.create_user("C", "D", "second@example.com")
        assert mock_repo.save.call_count == 2
        emails = [mock_repo.save.call_args_list[i][0][0].email for i in range(2)]
        assert "first@example.com" in emails
        assert "second@example.com" in emails
