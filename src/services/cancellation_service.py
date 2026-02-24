import logging

from src.exceptions.match_exceptions import MatchNotFoundError, NotInitiatorError
from src.models.enums import MatchRequestStatus, UserStatus
from src.repositories.interfaces.match_repository import MatchRepositoryInterface
from src.repositories.interfaces.token_repository import TokenRepositoryInterface
from src.repositories.interfaces.user_repository import UserRepositoryInterface
from src.services.email_service import EmailService

logger = logging.getLogger(__name__)


class CancellationService:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        match_repository: MatchRepositoryInterface,
        token_repository: TokenRepositoryInterface,
        email_service: EmailService,
    ) -> None:
        self._user_repo = user_repository
        self._match_repo = match_repository
        self._token_repo = token_repository
        self._email_service = email_service

    async def cancel_match(self, requesting_user_id: int, match_id: int) -> None:
        match_request = await self._match_repo.get_by_id(match_id)
        if match_request is None:
            raise MatchNotFoundError

        if match_request.initiator_id != requesting_user_id:
            raise NotInitiatorError

        await self._match_repo.update_status(match_id, MatchRequestStatus.CANCELLED)
        await self._user_repo.update_status(match_request.initiator_id, UserStatus.AVAILABLE)
        await self._user_repo.update_status(match_request.target_id, UserStatus.AVAILABLE)

        token = await self._token_repo.get_by_match_request_id(match_id)
        if token and not token.is_used:
            await self._token_repo.mark_used(token.id)

        initiator = await self._user_repo.get_by_id(match_request.initiator_id)
        target = await self._user_repo.get_by_id(match_request.target_id)

        await self._email_service.send_match_cancelled(initiator=initiator, target=target)

        logger.info(
            "Match cancelled by initiator: %s cancelled match with %s (match_id=%d)",
            initiator.full_name,
            target.full_name,
            match_id,
        )
