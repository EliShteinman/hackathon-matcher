from abc import ABC, abstractmethod

from src.models.enums import MatchRequestStatus
from src.models.match_request import MatchRequest


class MatchRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, match_request: MatchRequest) -> MatchRequest: ...

    @abstractmethod
    async def get_by_id(self, match_id: int) -> MatchRequest | None: ...

    @abstractmethod
    async def get_active_by_user_id(self, user_id: int) -> MatchRequest | None: ...

    @abstractmethod
    async def update_status(
        self, match_id: int, status: MatchRequestStatus, resolved_at: str | None = None
    ) -> None: ...
