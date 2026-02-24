from abc import ABC, abstractmethod

from src.models.token import EmailToken


class TokenRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, token: EmailToken) -> EmailToken: ...

    @abstractmethod
    async def get_by_uuid(self, uuid: str) -> EmailToken | None: ...

    @abstractmethod
    async def get_by_match_request_id(self, match_request_id: int) -> EmailToken | None: ...

    @abstractmethod
    async def mark_used(self, token_id: int) -> None: ...
