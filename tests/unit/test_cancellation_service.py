from unittest.mock import AsyncMock

import pytest

from src.exceptions.match_exceptions import MatchNotFoundError, NotInitiatorError
from src.models.enums import MatchRequestStatus
from src.models.match_request import MatchRequest
from src.models.token import EmailToken
from src.models.user import User
from src.services.cancellation_service import CancellationService


@pytest.fixture
def mock_user_repo():
    repo = AsyncMock()
    repo.get_by_id.return_value = User(id=1, id_number="111", email="a@t.com", full_name="Alice", branch="TLV")
    return repo


@pytest.fixture
def mock_match_repo():
    return AsyncMock()


@pytest.fixture
def mock_token_repo():
    return AsyncMock()


@pytest.fixture
def mock_email_service():
    return AsyncMock()


@pytest.fixture
def cancellation_service(mock_user_repo, mock_match_repo, mock_token_repo, mock_email_service):
    return CancellationService(mock_user_repo, mock_match_repo, mock_token_repo, mock_email_service)


class TestCancelMatch:
    async def test_match_not_found_raises(self, cancellation_service, mock_match_repo):
        mock_match_repo.get_by_id.return_value = None
        with pytest.raises(MatchNotFoundError):
            await cancellation_service.cancel_match(1, 999)

    async def test_non_initiator_raises(self, cancellation_service, mock_match_repo):
        mock_match_repo.get_by_id.return_value = MatchRequest(
            id=1, initiator_id=2, target_id=1, status=MatchRequestStatus.PENDING
        )
        with pytest.raises(NotInitiatorError):
            await cancellation_service.cancel_match(1, 1)

    async def test_successful_cancellation_pending(
        self, cancellation_service, mock_match_repo, mock_user_repo, mock_token_repo, mock_email_service
    ):
        mock_match_repo.get_by_id.return_value = MatchRequest(
            id=1, initiator_id=1, target_id=2, status=MatchRequestStatus.PENDING
        )
        mock_token_repo.get_by_match_request_id.return_value = EmailToken(
            id=1,
            uuid="abc",
            match_request_id=1,
            is_used=False,
            expires_at="2099-01-01T00:00:00",
        )
        await cancellation_service.cancel_match(1, 1)

        mock_match_repo.update_status.assert_called_once_with(1, MatchRequestStatus.CANCELLED)
        assert mock_user_repo.update_status.call_count == 2
        mock_token_repo.mark_used.assert_called_once_with(1)
        mock_email_service.send_match_cancelled.assert_called_once()

    async def test_successful_cancellation_approved(
        self, cancellation_service, mock_match_repo, mock_user_repo, mock_token_repo, mock_email_service
    ):
        mock_match_repo.get_by_id.return_value = MatchRequest(
            id=1, initiator_id=1, target_id=2, status=MatchRequestStatus.APPROVED
        )
        mock_token_repo.get_by_match_request_id.return_value = EmailToken(
            id=1,
            uuid="abc",
            match_request_id=1,
            is_used=True,
            expires_at="2099-01-01T00:00:00",
        )
        await cancellation_service.cancel_match(1, 1)

        mock_match_repo.update_status.assert_called_once_with(1, MatchRequestStatus.CANCELLED)
        mock_token_repo.mark_used.assert_not_called()
