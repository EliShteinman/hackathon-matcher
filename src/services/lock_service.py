import logging
from datetime import UTC, datetime

from src.exceptions.lock_exceptions import DeadlinePassedError, SystemLockedError
from src.repositories.interfaces.settings_repository import SettingsRepositoryInterface

logger = logging.getLogger(__name__)


class LockService:
    def __init__(self, settings_repository: SettingsRepositoryInterface) -> None:
        self._settings_repo = settings_repository

    async def is_locked(self) -> bool:
        settings = await self._settings_repo.get()
        if settings.is_globally_locked:
            return True
        return bool(settings.deadline and datetime.now(UTC) > settings.deadline)

    async def assert_not_locked(self) -> None:
        settings = await self._settings_repo.get()
        if settings.is_globally_locked:
            logger.warning("Operation blocked: system globally locked")
            raise SystemLockedError
        if settings.deadline and datetime.now(UTC) > settings.deadline:
            logger.warning("Operation blocked: deadline passed (%s)", settings.deadline)
            raise DeadlinePassedError
