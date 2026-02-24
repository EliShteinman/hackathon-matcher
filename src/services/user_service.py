import logging

from src.models.enums import UserStatus
from src.models.user import User
from src.repositories.interfaces.user_repository import UserRepositoryInterface

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repository: UserRepositoryInterface) -> None:
        self._user_repo = user_repository

    async def get_available_users(self, exclude_user_id: int) -> list[User]:
        return await self._user_repo.get_available_excluding(exclude_user_id)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self._user_repo.get_by_id(user_id)

    async def get_metrics(self) -> dict[UserStatus, int]:
        return await self._user_repo.count_by_status()

    async def get_all_users(self) -> list[User]:
        return await self._user_repo.get_all()
