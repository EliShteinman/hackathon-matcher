from unittest.mock import AsyncMock

import pytest

from src.exceptions.lock_exceptions import SystemLockedError
from src.exceptions.match_exceptions import AlreadyInMatchError, SelfMatchError, UserNotAvailableError
from src.models.enums import MatchRequestStatus, UserStatus
from src.models.match_request import MatchRequest
from src.models.user import User
from src.services.lock_service import LockService
from src.services.match_service import MatchService


@pytest.fixture
def mock_user_repo():
    repo = AsyncMock()
    repo.get_by_id.return_value = User(id=1, id_number="111", email="a@t.com", full_name="Alice", branch="TLV")
    return repo


@pytest.fixture
def mock_match_repo():
    repo = AsyncMock()
    repo.get_active_by_user_id.return_value = None
    repo.create.side_effect = lambda m: setattr(m, "id", 1) or m
    return repo


@pytest.fixture
def mock_token_repo():
    repo = AsyncMock()
    repo.create.side_effect = lambda t: setattr(t, "id", 1) or t
    return repo


@pytest.fixture
def mock_lock_service():
    svc = AsyncMock(spec=LockService)
    svc.assert_not_locked.return_value = None
    return svc


@pytest.fixture
def mock_email_service():
    return AsyncMock()


@pytest.fixture
def match_service(mock_user_repo, mock_match_repo, mock_token_repo, mock_lock_service, mock_email_service):
    return MatchService(
        user_repository=mock_user_repo,
        match_repository=mock_match_repo,
        token_repository=mock_token_repo,
        lock_service=mock_lock_service,
        email_service=mock_email_service,
    )


class TestInitiateMatch:
    async def test_self_match_raises(self, match_service: MatchService):
        with pytest.raises(SelfMatchError):
            await match_service.initiate_match(1, 1)

    async def test_locked_system_raises(self, match_service: MatchService, mock_lock_service):
        mock_lock_service.assert_not_locked.side_effect = SystemLockedError()
        with pytest.raises(SystemLockedError):
            await match_service.initiate_match(1, 2)

    async def test_already_in_match_raises(self, match_service: MatchService, mock_match_repo):
        mock_match_repo.get_active_by_user_id.return_value = MatchRequest(
            id=99, initiator_id=1, target_id=3, status=MatchRequestStatus.PENDING
        )
        with pytest.raises(AlreadyInMatchError):
            await match_service.initiate_match(1, 2)

    async def test_target_not_available_raises(self, match_service: MatchService, mock_user_repo):
        mock_user_repo.update_status_with_lock.return_value = False
        with pytest.raises(UserNotAvailableError):
            await match_service.initiate_match(1, 2)

    async def test_successful_match(
        self, match_service: MatchService, mock_user_repo, mock_match_repo, mock_email_service
    ):
        mock_user_repo.update_status_with_lock.return_value = True
        result = await match_service.initiate_match(1, 2)
        assert result.initiator_id == 1
        assert result.target_id == 2
        assert result.status == MatchRequestStatus.PENDING
        mock_email_service.send_match_request.assert_called_once()

    async def test_initiator_claim_fails_rolls_back_target(self, match_service: MatchService, mock_user_repo):
        mock_user_repo.update_status_with_lock.side_effect = [True, False]
        with pytest.raises(AlreadyInMatchError):
            await match_service.initiate_match(1, 2)
        mock_user_repo.update_status.assert_called_once_with(2, UserStatus.AVAILABLE)


class TestApproveMatch:
    async def test_approve_sets_matched(
        self, match_service: MatchService, mock_user_repo, mock_match_repo, mock_email_service
    ):
        mr = MatchRequest(id=1, initiator_id=1, target_id=2, status=MatchRequestStatus.PENDING)
        await match_service.approve_match(mr)
        mock_match_repo.update_status.assert_called_once_with(1, MatchRequestStatus.APPROVED)
        assert mock_user_repo.update_status.call_count == 2
        mock_email_service.send_match_approved.assert_called_once()


class TestRejectMatch:
    async def test_reject_resets_available(
        self, match_service: MatchService, mock_user_repo, mock_match_repo, mock_email_service
    ):
        mr = MatchRequest(id=1, initiator_id=1, target_id=2, status=MatchRequestStatus.PENDING)
        await match_service.reject_match(mr)
        mock_match_repo.update_status.assert_called_once_with(1, MatchRequestStatus.REJECTED)
        assert mock_user_repo.update_status.call_count == 2
        mock_email_service.send_match_rejected.assert_called_once()
