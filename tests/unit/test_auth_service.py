from unittest.mock import AsyncMock

import pytest

from src.exceptions.auth_exceptions import AdminAuthenticationError, InvalidCredentialsError, SessionExpiredError
from src.models.user import User
from src.services.auth_service import AuthService

SECRET = "test-secret-key"


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_user_repo):
    return AuthService(mock_user_repo, SECRET)


class TestAuthenticate:
    async def test_valid_credentials(self, auth_service, mock_user_repo):
        mock_user_repo.get_by_id_number_and_email.return_value = User(
            id=1, id_number="111", email="a@t.com", full_name="Alice", branch="TLV"
        )
        user = await auth_service.authenticate("111", "a@t.com")
        assert user.id == 1
        assert user.full_name == "Alice"

    async def test_invalid_credentials(self, auth_service, mock_user_repo):
        mock_user_repo.get_by_id_number_and_email.return_value = None
        with pytest.raises(InvalidCredentialsError):
            await auth_service.authenticate("999", "wrong@t.com")


class TestSessionToken:
    def test_create_and_verify(self, auth_service):
        token = auth_service.create_session_token(42)
        user_id = auth_service.verify_session_token(token)
        assert user_id == 42

    def test_invalid_token_raises(self, auth_service):
        with pytest.raises(SessionExpiredError):
            auth_service.verify_session_token("invalid-token")


class TestAdminToken:
    def test_create_and_verify(self, auth_service):
        token = auth_service.create_admin_token()
        result = auth_service.verify_admin_token(token)
        assert result is True


class TestAdminCredentials:
    def test_valid_credentials(self):
        AuthService.verify_admin_credentials("admin", "pass", "admin", "pass")

    def test_invalid_credentials(self):
        with pytest.raises(AdminAuthenticationError):
            AuthService.verify_admin_credentials("admin", "wrong", "admin", "pass")
