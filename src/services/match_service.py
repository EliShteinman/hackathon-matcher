import logging
import uuid
from datetime import UTC, datetime, timedelta

from src.exceptions.match_exceptions import AlreadyInMatchError, SelfMatchError, UserNotAvailableError
from src.models.enums import MatchRequestStatus, UserStatus
from src.models.match_request import MatchRequest
from src.models.token import EmailToken
from src.repositories.interfaces.match_repository import MatchRepositoryInterface
from src.repositories.interfaces.token_repository import TokenRepositoryInterface
from src.repositories.interfaces.user_repository import UserRepositoryInterface
from src.services.email_service import EmailService
from src.services.lock_service import LockService

logger = logging.getLogger(__name__)


class MatchService:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        match_repository: MatchRepositoryInterface,
        token_repository: TokenRepositoryInterface,
        lock_service: LockService,
        email_service: EmailService,
        token_expiry_hours: int = 72,
        base_url: str = "http://localhost:8000",
    ) -> None:
        self._user_repo = user_repository
        self._match_repo = match_repository
        self._token_repo = token_repository
        self._lock_service = lock_service
        self._email_service = email_service
        self._token_expiry_hours = token_expiry_hours
        self._base_url = base_url

    async def initiate_match(self, initiator_id: int, target_id: int) -> MatchRequest:
        if initiator_id == target_id:
            raise SelfMatchError

        await self._lock_service.assert_not_locked()

        existing = await self._match_repo.get_active_by_user_id(initiator_id)
        if existing:
            raise AlreadyInMatchError

        target_claimed = await self._user_repo.update_status_with_lock(
            target_id, UserStatus.AVAILABLE, UserStatus.PENDING
        )
        if not target_claimed:
            raise UserNotAvailableError

        initiator_claimed = await self._user_repo.update_status_with_lock(
            initiator_id, UserStatus.AVAILABLE, UserStatus.PENDING
        )
        if not initiator_claimed:
            await self._user_repo.update_status(target_id, UserStatus.AVAILABLE)
            raise AlreadyInMatchError

        match_request = MatchRequest(initiator_id=initiator_id, target_id=target_id)
        match_request = await self._match_repo.create(match_request)

        token_uuid = str(uuid.uuid4())
        email_token = EmailToken(
            uuid=token_uuid,
            match_request_id=match_request.id,
            expires_at=datetime.now(UTC) + timedelta(hours=self._token_expiry_hours),
        )
        await self._token_repo.create(email_token)

        initiator = await self._user_repo.get_by_id(initiator_id)
        target = await self._user_repo.get_by_id(target_id)

        await self._email_service.send_match_request(
            initiator=initiator,
            target=target,
            token_uuid=token_uuid,
            base_url=self._base_url,
        )

        logger.info(
            "Match initiated: %s -> %s (match_id=%d)",
            initiator.full_name,
            target.full_name,
            match_request.id,
        )
        return match_request

    async def approve_match(self, match_request: MatchRequest) -> None:
        await self._match_repo.update_status(match_request.id, MatchRequestStatus.APPROVED)
        await self._user_repo.update_status(match_request.initiator_id, UserStatus.MATCHED)
        await self._user_repo.update_status(match_request.target_id, UserStatus.MATCHED)

        initiator = await self._user_repo.get_by_id(match_request.initiator_id)
        target = await self._user_repo.get_by_id(match_request.target_id)

        await self._email_service.send_match_approved(initiator=initiator, target=target)

        logger.info("Match approved: %s <-> %s (match_id=%d)", initiator.full_name, target.full_name, match_request.id)

    async def reject_match(self, match_request: MatchRequest) -> None:
        await self._match_repo.update_status(match_request.id, MatchRequestStatus.REJECTED)
        await self._user_repo.update_status(match_request.initiator_id, UserStatus.AVAILABLE)
        await self._user_repo.update_status(match_request.target_id, UserStatus.AVAILABLE)

        initiator = await self._user_repo.get_by_id(match_request.initiator_id)
        target = await self._user_repo.get_by_id(match_request.target_id)

        await self._email_service.send_match_rejected(initiator=initiator, target=target)

        logger.info(
            "Match rejected: %s rejected %s (match_id=%d)", target.full_name, initiator.full_name, match_request.id
        )
