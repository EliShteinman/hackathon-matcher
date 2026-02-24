from abc import ABC, abstractmethod

from src.models.enums import UserStatus
from src.models.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_id_number_and_email(self, id_number: str, email: str) -> User | None: ...

    @abstractmethod
    async def get_available_excluding(self, exclude_user_id: int) -> list[User]: ...

    @abstractmethod
    async def update_status(self, user_id: int, new_status: UserStatus) -> None: ...

    @abstractmethod
    async def update_status_with_lock(
        self, user_id: int, expected_status: UserStatus, new_status: UserStatus
    ) -> bool: ...

    @abstractmethod
    async def bulk_upsert(self, users: list[User]) -> int: ...

    @abstractmethod
    async def count_by_status(self) -> dict[UserStatus, int]: ...

    @abstractmethod
    async def get_all(self) -> list[User]: ...
