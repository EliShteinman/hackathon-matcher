import logging
from datetime import UTC, datetime

from src.exceptions.token_exceptions import TokenAlreadyUsedError, TokenExpiredError, TokenNotFoundError
from src.models.match_request import MatchRequest
from src.models.token import EmailToken
from src.repositories.interfaces.match_repository import MatchRepositoryInterface
from src.repositories.interfaces.token_repository import TokenRepositoryInterface
from src.services.match_service import MatchService

logger = logging.getLogger(__name__)


class TokenService:
    def __init__(
        self,
        token_repository: TokenRepositoryInterface,
        match_repository: MatchRepositoryInterface,
        match_service: MatchService,
    ) -> None:
        self._token_repo = token_repository
        self._match_repo = match_repository
        self._match_service = match_service

    async def _validate_token(self, uuid: str) -> tuple[EmailToken, MatchRequest]:
        token = await self._token_repo.get_by_uuid(uuid)
        if token is None:
            raise TokenNotFoundError
        if token.is_used:
            raise TokenAlreadyUsedError
        if datetime.now(UTC) > token.expires_at:
            raise TokenExpiredError

        match_request = await self._match_repo.get_by_id(token.match_request_id)
        if match_request is None:
            raise TokenNotFoundError

        return token, match_request

    async def get_token_details(self, uuid: str) -> tuple[EmailToken, MatchRequest]:
        token = await self._token_repo.get_by_uuid(uuid)
        if token is None:
            raise TokenNotFoundError
        match_request = await self._match_repo.get_by_id(token.match_request_id)
        if match_request is None:
            raise TokenNotFoundError
        return token, match_request

    async def approve(self, uuid: str) -> None:
        token, match_request = await self._validate_token(uuid)
        await self._token_repo.mark_used(token.id)
        await self._match_service.approve_match(match_request)
        logger.info("Token %s: match %d approved", uuid, match_request.id)

    async def reject(self, uuid: str) -> None:
        token, match_request = await self._validate_token(uuid)
        await self._token_repo.mark_used(token.id)
        await self._match_service.reject_match(match_request)
        logger.info("Token %s: match %d rejected", uuid, match_request.id)
